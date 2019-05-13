import ROOT
from ROOT import TFile
import sys
import time
from PyBGSuggestHelpers import TimeClass
import ImportHelpers

MyTime = TimeClass()

##
## This converts the csv format of Medtronic (the version that has 39 entries) to root TTree format.
## It no longer works for the current Medtronic csv export. Use Tidepool (jsonToRoot.py) instead.
##

rootfilename = 'output.root'
datadir = 'data'

import os
thedir = os.listdir(datadir)
inputfilenames = []
for d in thedir :
    if 'Export' in d and 'csv' in d : 
        inputfilenames.append('%s/%s'%(datadir,d))

inputfilenames = sorted(inputfilenames)
print inputfilenames

ROOT.gROOT.LoadMacro('bgrootstruct.h+')

rootfile = TFile(rootfilename,"RECREATE")

tree = ROOT.TTree("FullResults","Full Results")
s = ROOT.bgrootstruct()

basal_histograms = ImportHelpers.SettingsHistograms('Basal')
sensi_histograms = ImportHelpers.SettingsHistograms('Sensitivity')
ric_histograms = ImportHelpers.SettingsHistograms('RIC')

##
## Stuff for studing MARD and stuff.
##
sensor_age_utc = 0
sensor_isig_age = 0
sensor_isig = -1
sensor_bg = -1

branches = ImportHelpers.GetTreeBranchClassesDict()

for br in branches.keys() :
    #print '%s/%s'%(br,branches[br].btype)
    tree.Branch(br,ROOT.AddressOf(s,br),'%s/%s'%(br,branches[br].btype))

#
# Add Derived values to detailed tree
#
ImportHelpers.AddTimeBranchesToTree(tree,s)
ImportHelpers.AddTimeCourtesyBranchesToTree(tree,s)

#
# Long-term data, which saves only a subset of the data.
#
rootfile_all = TFile('output_all.root','RECREATE')
tree2 = ROOT.TTree("LongTerm","LongTerm")
s2 = ROOT.bgrootstruct()

ImportHelpers.AddTimeBranchesToTree(tree2,s2)
ImportHelpers.AddBasicBranchesToTree(tree2,s2)

import time
time_right_now = long(time.time())

for inputfilename in inputfilenames :

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
            start_time = int(2*int(linevector[34].split()[i_st].replace('START_TIME=',''))/3600000)
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

        for br in ['Index','Date','Time','Timestamp'] :
            val = linevector[branches[br].csvIndex]
            setattr(s,br,branches[br].formatValue(val))

        s.UniversalTime           = MyTime.TimeFromString(linevector[3])

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
            linevector[21] = ric_histograms.GetSettingFromHistogram(MyTime.GetTimeOfDay(s.UniversalTime))
            linevector[22] = sensi_histograms.GetSettingFromHistogram(MyTime.GetTimeOfDay(s.UniversalTime))

        #
        # For the Year-In-Review plot
        #
        s2.UniversalTime = MyTime.TimeFromString(linevector[3])
        s2.WeekOfYear = MyTime.GetWeekOfYear(s.UniversalTime)
        for br in ['BGReading','BWZCarbInput','Rewind'] :
            setattr(s2,br, branches[br].getFormattedValueFromVector(linevector) )

        #
        # get new sensor time (UTC) - for cumulative plots
        #
        if 'SensorSync' in linevector[33] and 'SYNC_TYPE=new' in linevector[34] :
            sensor_age_utc = s.UniversalTime
        #
        # temporarily store last sensor measurement
        #
        if 'GlucoseSensorData' in linevector[33] :
           sensor_isig_age = s.UniversalTime
           sensor_isig = branches['ISIGValue'].getFormattedValueFromVector(linevector)
           sensor_bg = branches['SensorGlucose'].getFormattedValueFromVector(linevector)

        #
        # s2.BGReading > 0
        #
        if s2.BGReading > 0 and ((s.UniversalTime-sensor_isig_age)/float(MyTime.OneMinute) <= 5.) :
            #print 'age:',(s.UniversalTime-sensor_isig_age)/float(MyTime.OneMinute),
            #print 'isig:',sensor_isig,'bg:',sensor_bg
            s2.RecentSensorISIG = sensor_isig
            s2.RecentSensorGlucose = sensor_bg
            s2.MARD = (sensor_bg - s2.BGReading)/float(s2.BGReading)
            s2.SensorAgeDays = (s.UniversalTime-sensor_age_utc)/float(MyTime.OneDay)
        else :
            s2.RecentSensorISIG = -1.
            s2.RecentSensorGlucose = -1
            s2.MARD = -100.
            s2.SensorAgeDays = -1.

        if s2.BGReading > 0 or s2.BWZFoodEstimate > 0 or s2.Rewind :
            tree2.Fill()

        #
        # If it's older than 4 weeks old, do not do a detailed review.
        #
        print '%s %d \r'%(MyTime.StringFromTime(s.UniversalTime),MyTime.WeeksOld(s.UniversalTime)),
        if MyTime.WeeksOld(s.UniversalTime) > 4 :
            continue

        s.WeekOfYear              = MyTime.GetWeekOfYear(s.UniversalTime)
        s.DayOfWeekFromMonday     = MyTime.GetDayOfWeek(s.UniversalTime)
        s.HourOfDayFromFourAM     = MyTime.GetHourOfDay(s.UniversalTime)
        s.TimeOfDayFromFourAM     = float(MyTime.GetTimeOfDay(s.UniversalTime))

        # Fill the rest of the branches.
        for br in ['NewDeviceTime','BGReading','TempBasalAmount','TempBasalType',
                   'TempBasalDuration','BolusType','BolusVolumeSelected',
                   'BolusVolumeDelivered','ProgrammedBolusDuration','PrimeType',
                   'PrimeVolumeDelivered','Suspend','Rewind','BWZEstimate','BWZTargetHighBG',
                   'BWZTargetLowBG','BWZCarbRatio','BWZInsulinSensitivity','BWZCarbInput',
                   'BWZBGInput','BWZCorrectionEstimate','BWZFoodEstimate','BWZActiveInsulin',
                   'Alarm','SensorCalibrationBG','SensorGlucose','ISIGValue','DailyInsulinTotal',
                   'RawType','RawValues','RawID','RawUploadID','RawSeqNum','RawDeviceType'] :
            setattr(s,br, branches[br].getFormattedValueFromVector(linevector) )

        tree.Fill()

print

for settings_class in [basal_histograms,sensi_histograms,ric_histograms] :
    settings_class.WriteToFile(rootfile)
    settings_class.WriteToFile(rootfile_all)

rootfile.Write()
rootfile.Close()

rootfile_all.Write()
rootfile_all.Close()
