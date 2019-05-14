import ROOT
import sys
import time
from PyBGSuggestHelpers import MyTime
import ImportHelpers
from ImportHelpers import branches
from ImportHelpers import dataStorageInstance as storage

##
## This converts the csv format of Medtronic (the version that has 39 entries) to root TTree format.
## It no longer works for the current Medtronic csv export. Use Tidepool (jsonToRoot.py) instead.
##

def main(options,args) :

    # All of the setup is now done in this wrapper function
    manager = ImportHelpers.ImportManager(options,args)
    inputfilenames = manager.GetInputFiles()

    for inputfilename in inputfilenames :
        manager.ProcessFile(inputfilename,ProcessFileCSV)

    # Save output
    manager.Finish()

    return

def ProcessFileCSV(inputfilename,treeDetailed,sDetailed,
                   treeSummary,sSummary,
                   basal_histograms,sensi_histograms,ric_histograms,
                   options) :

    inputfile = open(inputfilename,'r')
    for line in inputfile:

        # Get rid of commas between quoted items
        linevector = line.split('"')
        for i in range(len(linevector)) :
            if not i%2 :
                continue
            linevector[i] = linevector[i].replace(',','')
        line = ''.join(linevector)

        linevector = line.split(',')
        if len(linevector)<20:
            continue

        #
        # Collect basal, sensitivity, insulin-carb ratio information
        #
        if linevector[33] in ['ChangeBasalProfile','ChangeInsulinSensitivity','ChangeCarbRatio'] :

            # PATTERN_DATUM_ID=15906088830 PROFILE_INDEX=11 RATE=0.9 START_TIME=79200000
            # Start time is in hours, from midnight.
            # START_TIME is either index number 4 or 3:
            i_st = 4 if linevector[33] == 'ChangeCarbRatio' else 3

            start_time_milliseconds = linevector[34].split()[i_st].replace('START_TIME=','')
            start_time = start_time_milliseconds / MyTime.MillisecondsInAnHour
            timestamp = linevector[3]

            if linevector[33] == 'ChangeBasalProfile' :
                rate = float(linevector[34].split()[2].replace('RATE=',''))
                basal_histograms.AddSettingToHistogram(timestamp,start_time,rate)

            if linevector[33] == 'ChangeInsulinSensitivity' :
                rate = float(linevector[34].split()[2].replace('AMOUNT=',''))
                sensi_histograms.AddSettingToHistogram(timestamp,start_time,rate)

            if linevector[33] == 'ChangeCarbRatio' :
                ric = float(linevector[34].split()[2].replace('AMOUNT=',''))
                ric_histograms.AddSettingToHistogram(timestamp,start_time,ric)

        #
        # The standard data collection.
        #
        isDataLine = (len(linevector) == 39) and (linevector[0] != "Index")
        if not isDataLine :
            continue

        uTime = MyTime.TimeFromString(linevector[3])

        #
        # We take only the "BGReceived" BG data, to avoid double-counting.
        # linevector[5] = BGReading and linevector[6] = LinkedBGMeterID
        #
        if linevector[5] and (not str(linevector[6])) :
            continue

        #
        # For JournalEntryMealMarker we enter that into the BWZEstimate entry.
        # The text field is linevector[33]
        if 'JournalEntryMealMarker' in linevector[33] :
            # Hack to save carbs [23], carb ratio [21] and sensitivity [22]:
            linevector[23] = line.split('CARB_INPUT=')[1].split(',')[0].split()[0]
            linevector[21] = ric_histograms.GetSettingFromHistogram(MyTime.GetTimeOfDay(uTime))
            linevector[22] = sensi_histograms.GetSettingFromHistogram(MyTime.GetTimeOfDay(uTime))

        #
        # For the Year-In-Review plot
        #
        sSummary.UniversalTime = uTime
        sSummary.WeekOfYear = MyTime.GetWeekOfYear(uTime)
        for br in ['BGReading','BWZCarbInput','Rewind'] :
            setattr(sSummary,br, branches[br].getFormattedValueFromVector(linevector) )

        #
        # get new sensor time (UTC) - for cumulative plots
        #
        if 'SensorSync' in linevector[33] and 'SYNC_TYPE=new' in linevector[34] :
            storage.current_sensor_age_utc = uTime
        #
        # temporarily store last sensor measurement
        #
        if 'GlucoseSensorData' in linevector[33] :
            storage.last_sensor_isig_age = uTime
            storage.last_sensor_isig = branches['ISIGValue'].getFormattedValueFromVector(linevector)
            storage.last_sensor_bg = branches['SensorGlucose'].getFormattedValueFromVector(linevector)

        #
        # sSummary.BGReading > 0
        #
        age_of_last_isig_minutes = (uTime-storage.last_sensor_isig_age)/float(MyTime.OneMinute)

        if sSummary.BGReading > 0 and (age_of_last_isig_minutes <= 5.) :
            sSummary.RecentSensorISIG = storage.last_sensor_isig
            sSummary.RecentSensorGlucose = storage.last_sensor_bg
            sSummary.MARD = (storage.last_sensor_bg - sSummary.BGReading)/float(sSummary.BGReading)
            sSummary.SensorAgeDays = (uTime-storage.current_sensor_age_utc)/float(MyTime.OneDay)
        else :
            sSummary.RecentSensorISIG = -1.
            sSummary.RecentSensorGlucose = -1
            sSummary.MARD = -100.
            sSummary.SensorAgeDays = -1.

        if sSummary.BGReading > 0 or sSummary.BWZFoodEstimate > 0 or sSummary.Rewind :
            treeSummary.Fill()

        #
        # If it's older than 4 weeks old, do not do a detailed review.
        #
        print '%s %d \r'%(MyTime.StringFromTime(uTime),MyTime.WeeksOld(uTime)),
        if MyTime.WeeksOld(uTime) > options.ndetailed :
            continue

        for br in ['Index','Date','Time','Timestamp'] :
            val = linevector[branches[br].csvIndex]
            setattr(sDetailed,br,branches[br].formatCSVValue(val))

        sDetailed.UniversalTime = uTime
        sDetailed.WeekOfYear              = MyTime.GetWeekOfYear(uTime)
        sDetailed.DayOfWeekFromMonday     = MyTime.GetDayOfWeek(uTime)
        sDetailed.HourOfDayFromFourAM     = MyTime.GetHourOfDay(uTime)
        sDetailed.TimeOfDayFromFourAM     = float(MyTime.GetTimeOfDay(uTime))

        # Fill the rest of the branches.
        for br in ['NewDeviceTime','BGReading','TempBasalAmount','TempBasalType',
                   'TempBasalDuration','BolusType','BolusVolumeSelected',
                   'BolusVolumeDelivered','ProgrammedBolusDuration','PrimeType',
                   'PrimeVolumeDelivered','Suspend','Rewind','BWZEstimate','BWZTargetHighBG',
                   'BWZTargetLowBG','BWZCarbRatio','BWZInsulinSensitivity','BWZCarbInput',
                   'BWZBGInput','BWZCorrectionEstimate','BWZFoodEstimate','BWZActiveInsulin',
                   'Alarm','SensorCalibrationBG','SensorGlucose','ISIGValue','DailyInsulinTotal',
                   'RawType','RawValues','RawID','RawUploadID','RawSeqNum','RawDeviceType'] :
            setattr(sDetailed,br, branches[br].getFormattedValueFromVector(linevector) )

        treeDetailed.Fill()

    return

if __name__ == '__main__' :
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--ndetailed',type='int',default=4,dest='ndetailed',help='Number of weeks of detail (4)')
    p.add_option('--outname'  ,type='string',default='output_medtronic.root',dest='outname',help='Output root file name')
    p.add_option('--datadir'  ,type='string',default='data',dest='datadir',help='Data directory')

    options,args = p.parse_args()

    # We will only process Medtronic csv files:
    options.match_regexp = ['CareLink_Export.*csv']

    main(options,args)
