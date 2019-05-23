import ROOT
import sys
import time
from TimeClass import MyTime
import ImportHelpers
from ImportHelpers import branches
from ImportHelpers import dataStorageInstance as storage
import json

##
## This converts the json format of TidePool to root TTree format.
##

def main(options,args) :

    # All of the setup is now done in this wrapper function
    manager = ImportHelpers.ImportManager(options,args)
    inputfilenames = manager.GetInputFiles()

    for inputfilename in inputfilenames :
        manager.ProcessFile(inputfilename,ProcessFileJSON)

    # Save output
    manager.Finish()

    return

def ResetAddresses(bgstruct) :
    # reset addresses:
    for br in dir(bgstruct) :
        if '__' in br :
            continue
        if br in branches.keys() :
            setattr(bgstruct,br,branches[br].DefaultValue())
        elif type(getattr(bgstruct,br)) == type(long(1)) :
            setattr(bgstruct,br,0)
        else :
            setattr(bgstruct,br,-1)
    return

def ToMgDL(value,cfactor) :
    if cfactor == 1 :
        return value
    return int( round(value * cfactor) )

def ProcessFileJSON(inputfilename,treeDetailed,sDetailed,
                    treeSummary,sSummary,
                    basal_histograms,sensi_histograms,ric_histograms,duration_histograms,
                    options) :

    keys = []
    json_file = open(inputfilename)

    data = json.load(json_file)

    # Process from earliest to latest
    for line in reversed(data) :

        if 'deviceTime' not in line.keys() :
            continue

        # reset addresses:
        ResetAddresses(sDetailed)
        ResetAddresses(sSummary)

        for j in line.keys() :
            if j in keys :
                continue
            keys.append(j)

        uTime = MyTime.TimeFromString(line['deviceTime'])

        #
        # Summary info (long-term)
        #
        sSummary.UniversalTime = uTime
        sSummary.WeekOfYear = MyTime.GetWeekOfYear(uTime)

        # Conversion from mmol/L to mg/dL (found in TidePool code)
        cfactor = 1
        if line.get('units',None) == 'mmol/L' or line.get('units',{}).get('bg',None) == 'mmol/L' :
            cfactor = 18.01559

        itype = line.get('type',None)

        #
        # Collect basal, sensitivity, insulin-carb ratio information
        #
        if itype == 'pumpSettings' :
            timestamp = line['deviceTime']

            duration = line["bolus"]["calculator"]["insulin"]["duration"]
            if not duration_histograms.hist_list :
                # There is only one per day.
                duration_histograms.AddSettingToHistogram(timestamp,0,duration)
            elif duration != duration_histograms.GetSettingFromHistogram(0) :
                duration_histograms.AddSettingToHistogram(timestamp,0,duration)

            for entries in line['basalSchedules']['standard'] :
                start_time = entries['start'] / float(MyTime.MillisecondsInAnHour)
                basal_histograms.AddSettingToHistogram(timestamp,start_time,entries['rate'])

            for entries in line['insulinSensitivity'] :
                start_time = entries['start'] / float(MyTime.MillisecondsInAnHour)
                amount = ToMgDL(entries['amount'],cfactor)
                sensi_histograms.AddSettingToHistogram(timestamp,start_time,amount)

            for entries in line['carbRatio'] :
                start_time = entries['start'] / float(MyTime.MillisecondsInAnHour)
                ric_histograms.AddSettingToHistogram(timestamp,start_time,entries['amount'])

        #
        # Rewind, BGReading
        #
        elif itype == 'deviceEvent' and line['subType'] == 'reservoirChange' :
            sSummary.Rewind = 1
        elif itype == 'smbg' :
            sSummary.BGReading = ToMgDL(line.get('value'),cfactor)

        if sSummary.BGReading > 0 or sSummary.BWZFoodEstimate > 0 or sSummary.Rewind :
            if options.summary :
                treeSummary.Fill()

        #
        # If it's older than 4 weeks old, do not do a detailed review.
        #
        print '%s %d \r'%(MyTime.StringFromTime(uTime),MyTime.WeeksOld(uTime)),
        if MyTime.WeeksOld(uTime) > options.ndetailed :
            continue

        #
        # Filling the detailed info, below:
        #
        sDetailed.UniversalTime       = uTime
        sDetailed.WeekOfYear          = MyTime.GetWeekOfYear(uTime)
        sDetailed.DayOfWeekFromMonday = MyTime.GetDayOfWeek(uTime)
        sDetailed.HourOfDayFromFourAM = MyTime.GetHourOfDay(uTime)
        sDetailed.TimeOfDayFromFourAM = float(MyTime.GetTimeOfDay(uTime))

        sDetailed.BGReading = sSummary.BGReading
        sDetailed.Rewind    = sSummary.Rewind

        if itype == 'bolus' :
            # to-do: handle subType
            if line['subType'] == 'normal' :
                sDetailed.BolusVolumeDelivered = line[line['subType']] # bolus volume Delivered? Selected?
            elif line['subType'] == 'square' :
                sDetailed.BolusVolumeDelivered = line['extended'] # bolus volume Delivered? Selected?
                sDetailed.ProgrammedBolusDuration = line['duration'] / MyTime.MillisecondsInAnHour
            else :
                print 'Error - need to handle %s (non-normal) subType!'%(line['subType'])
                print line
                import sys; sys.exit()

        elif itype == 'wizard' :
            sDetailed.BWZEstimate = line['recommended']['net']
            sDetailed.BWZTargetHighBG = ToMgDL(line['bgTarget']['high'],cfactor)
            sDetailed.BWZTargetLowBG  = ToMgDL(line['bgTarget']['low'] ,cfactor)
            sDetailed.BWZCarbRatio = line['insulinCarbRatio']
            sDetailed.BWZInsulinSensitivity = ToMgDL(line['insulinSensitivity'],cfactor)
            sDetailed.BWZCarbInput = line['carbInput']
            sDetailed.BWZBGInput   = ToMgDL(line.get('bgInput',0),cfactor)
            sDetailed.BWZCorrectionEstimate = line['recommended']['correction']
            sDetailed.BWZFoodEstimate = line['recommended']['carb']
            if 'insulinOnBoard' in line.keys() :
                sDetailed.BWZActiveInsulin = line['insulinOnBoard']

        # Temp basal
        elif itype == 'basal' :
            if line['deliveryType'] == 'temp':
                if storage.temp_basal_in_progress :
                    continue
                sDetailed.TempBasalType = 'Percent' if line.get('percent',None) else 'Unknown'
                if sDetailed.TempBasalType == 'Unknown' :
                    sDetailed.TempBasalAmount = round(line['rate']/float(line['suppressed']['rate']),2)
                    #print 'Warning - need to handle unknown (not Percent). For now, setting percent to %.2f'%(sDetailed.TempBasalAmount)
                else :
                    sDetailed.TempBasalAmount = round(line['percent'],2)
                sDetailed.TempBasalDuration = line['duration'] / MyTime.MillisecondsInAnHour
                storage.temp_basal_in_progress = True

            # Cancel a temp-basal-in-progress, for any non-temp basal
            elif storage.temp_basal_in_progress == True :
                sDetailed.TempBasalEnd = True
                storage.temp_basal_in_progress = False

            # In any case, cancel a suspend-in-progress
            if storage.suspend_in_progress == True :
                sDetailed.SuspendEnd = True
                storage.suspend_in_progress = False

        # Suspend (start)
        elif itype == 'deviceEvent' :
            if 'status' in line.keys() and line['status'] == 'suspended' :
                sDetailed.SuspendStart = True
                storage.suspend_in_progress = True

        treeDetailed.Fill()

    if False :
        print keys
    return

if __name__ == '__main__' :
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--summary' ,action='store_true',default=False,dest='summary' ,help='Make summary root file')
    p.add_option('--ndetailed',type='int',default=4,dest='ndetailed',help='Number of weeks of detail (4)')
    p.add_option('--outname'  ,type='string',default='output_tidepool.root',dest='outname',help='Output root file name')
    p.add_option('--datadir'  ,type='string',default='data',dest='datadir',help='Data directory')

    options,args = p.parse_args()

    # We will only process Tidepool json files:
    options.match_regexp = ['Tidepool_Export.*json']

    main(options,args)
