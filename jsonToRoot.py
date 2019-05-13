import ROOT
import sys
import time
from PyBGSuggestHelpers import MyTime
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
                    basal_histograms,sensi_histograms,ric_histograms,
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
        if line.get('units',None) == 'mmol/L' :
            cfactor = 18.01559

        itype = line.get('type',None)

        if itype == 'smbg' :
            sSummary.BGReading = ToMgDL(line.get('value'),cfactor)

        #
        # If it's older than 4 weeks old, do not do a detailed review.
        #
        #print '%s %d \r'%(MyTime.StringFromTime(uTime),MyTime.WeeksOld(uTime)),
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

        if itype == 'bolus' :
            # to-do: handle subType
            if line['subType'] != 'normal' :
                print 'Error - need to handle %s (non-normal) subType!'%(line['subType'])
                import sys; sys.exit()
            sDetailed.BolusVolumeDelivered = line[line['subType']] # bolus volume Delivered? Selected?

        elif itype == 'wizard' :
            sDetailed.BWZTargetHighBG = ToMgDL(line['bgTarget']['high'],cfactor)
            sDetailed.BWZTargetLowBG  = ToMgDL(line['bgTarget']['low'] ,cfactor)
            sDetailed.BWZInsulinSensitivity = ToMgDL(line['insulinSensitivity'],cfactor)
            sDetailed.BWZCarbInput = line['carbInput']
            sDetailed.BWZCarbRatio = line['insulinCarbRatio']
            sDetailed.BWZBGInput   = ToMgDL(line.get('bgInput',0),cfactor)

        treeDetailed.Fill()

    print keys
    return

if __name__ == '__main__' :
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--ndetailed',type='int',default=4,dest='ndetailed',help='Number of weeks of detail (4)')
    p.add_option('--outname'  ,type='string',default='output_tidepool.root',dest='outname',help='Output root file name')
    p.add_option('--datadir'  ,type='string',default='data',dest='datadir',help='Data directory')

    options,args = p.parse_args()

    # We will only process Tidepool json files:
    options.match_regexp = ['Tidepool_Export.*json']

    main(options,args)