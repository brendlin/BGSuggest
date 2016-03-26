import ROOT
from ROOT import TFile
import sys
import time
from PyBGSuggestHelpers import TimeClass

MyTime = TimeClass()

# if len(sys.argv) > 1:
#     #inputfilename = "/Volumes/Untitled/Users/k.brendlinger/Desktop/Carelink/"+str(sys.argv[1])
#     inputfilename = str(sys.argv[1])
#     rootfilename = str(sys.argv[1])
# else:
#     print "Error: No input file name specified. Exiting."
#     inputfilename = "test_export.csv"
#     rootfilename = inputfilename.replace('.csv','.root')

rootfilename = 'output.root'

import os
thedir = os.listdir('data')
inputfilenames = []
for d in thedir :
    if 'Export' in d and 'csv' in d : 
        inputfilenames.append('data/'+d)

inputfilenames = sorted(inputfilenames)

print inputfilenames

ROOT.gROOT.LoadMacro('bgrootstruct.h+')

rootfile = TFile(rootfilename,"RECREATE")
isNumber = [1,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0]

tree = ROOT.TTree("Tree Name","Tree Description")
s = ROOT.bgrootstruct()
#tree._s = s

basal_histograms = []
sensi_histograms = []
ric_histograms = []

tree.Branch("Index"                  ,ROOT.AddressOf(s,"Index"                  ),"Index"                  +"/I")
tree.Branch("Date"                   ,ROOT.AddressOf(s,"Date"                   ),"Date"                   +"/C") ###
tree.Branch("Time"                   ,ROOT.AddressOf(s,"Time"                   ),"Time"                   +"/C") ###
tree.Branch("Timestamp"              ,ROOT.AddressOf(s,"Timestamp"              ),"Timestamp"              +"/C") ###
tree.Branch("NewDeviceTime"          ,ROOT.AddressOf(s,"NewDeviceTime"          ),"NewDeviceTime"          +"/C") ###
tree.Branch("BGReading"              ,ROOT.AddressOf(s,"BGReading"              ),"BGReading"              +"/I")
tree.Branch("LinkedBGMeterID"        ,ROOT.AddressOf(s,"LinkedBGMeterID"        ),"LinkedBGMeterID"        +"/L")
tree.Branch("TempBasalAmount"        ,ROOT.AddressOf(s,"TempBasalAmount"        ),"TempBasalAmount"        +"/F")
tree.Branch("TempBasalType"          ,ROOT.AddressOf(s,"TempBasalType"          ),"TempBasalType"          +"/C") ###
tree.Branch("TempBasalDuration"      ,ROOT.AddressOf(s,"TempBasalDuration"      ),"TempBasalDuration"      +"/C") ###
tree.Branch("BolusType"              ,ROOT.AddressOf(s,"BolusType"              ),"BolusType"              +"/C") ###
tree.Branch("BolusVolumeSelected"    ,ROOT.AddressOf(s,"BolusVolumeSelected"    ),"BolusVolumeSelected"    +"/F")
tree.Branch("BolusVolumeDelivered"   ,ROOT.AddressOf(s,"BolusVolumeDelivered"   ),"BolusVolumeDelivered"   +"/F")
tree.Branch("ProgrammedBolusDuration",ROOT.AddressOf(s,"ProgrammedBolusDuration"),"ProgrammedBolusDuration"+"/C") ###
tree.Branch("PrimeType"              ,ROOT.AddressOf(s,"PrimeType"              ),"PrimeType"              +"/C") ###
tree.Branch("PrimeVolumeDelivered"   ,ROOT.AddressOf(s,"PrimeVolumeDelivered"   ),"PrimeVolumeDelivered"   +"/F")
tree.Branch("Suspend"                ,ROOT.AddressOf(s,"Suspend"                ),"Suspend"                +"/C") ###
tree.Branch("Rewind"                 ,ROOT.AddressOf(s,"Rewind"                 ),"Rewind"                 +"/I") # Changed
tree.Branch("BWZEstimate"            ,ROOT.AddressOf(s,"BWZEstimate"            ),"BWZEstimate"            +"/F")
tree.Branch("BWZTargetHighBG"        ,ROOT.AddressOf(s,"BWZTargetHighBG"        ),"BWZTargetHighBG"        +"/I")
tree.Branch("BWZTargetLowBG"         ,ROOT.AddressOf(s,"BWZTargetLowBG"         ),"BWZTargetLowBG"         +"/I")
tree.Branch("BWZCarbRatio"           ,ROOT.AddressOf(s,"BWZCarbRatio"           ),"BWZCarbRatio"           +"/F")
tree.Branch("BWZInsulinSensitivity"  ,ROOT.AddressOf(s,"BWZInsulinSensitivity"  ),"BWZInsulinSensitivity"  +"/I")
tree.Branch("BWZCarbInput"           ,ROOT.AddressOf(s,"BWZCarbInput"           ),"BWZCarbInput"           +"/I")
tree.Branch("BWZBGInput"             ,ROOT.AddressOf(s,"BWZBGInput"             ),"BWZBGInput"             +"/I")
tree.Branch("BWZCorrectionEstimate"  ,ROOT.AddressOf(s,"BWZCorrectionEstimate"  ),"BWZCorrectionEstimate"  +"/F")
tree.Branch("BWZFoodEstimate"        ,ROOT.AddressOf(s,"BWZFoodEstimate"        ),"BWZFoodEstimate"        +"/F")
tree.Branch("BWZActiveInsulin"       ,ROOT.AddressOf(s,"BWZActiveInsulin"       ),"BWZActiveInsulin"       +"/F")
tree.Branch("Alarm"                  ,ROOT.AddressOf(s,"Alarm"                  ),"Alarm"                  +"/C") ###
tree.Branch("SensorCalibrationBG"    ,ROOT.AddressOf(s,"SensorCalibrationBG"    ),"SensorCalibrationBG"    +"/I")
tree.Branch("SensorGlucose"          ,ROOT.AddressOf(s,"SensorGlucose"          ),"SensorGlucose"          +"/I")
tree.Branch("ISIGValue"              ,ROOT.AddressOf(s,"ISIGValue"              ),"ISIGValue"              +"/F")
tree.Branch("DailyInsulinTotal"      ,ROOT.AddressOf(s,"DailyInsulinTotal"      ),"DailyInsulinTotal"      +"/F")
tree.Branch("RawType"                ,ROOT.AddressOf(s,"RawType"                ),"RawType"                +"/C") ###
tree.Branch("RawValues"              ,ROOT.AddressOf(s,"RawValues"              ),"RawValues"              +"/C") ###
tree.Branch("RawID"                  ,ROOT.AddressOf(s,"RawID"                  ),"RawID"                  +"/L")
tree.Branch("RawUploadID"            ,ROOT.AddressOf(s,"RawUploadID"            ),"RawUploadID"            +"/L")
tree.Branch("RawSeqNum"              ,ROOT.AddressOf(s,"RawSeqNum"              ),"RawSeqNum"              +"/L")
tree.Branch("RawDeviceType"          ,ROOT.AddressOf(s,"RawDeviceType"          ),"RawDeviceType"          +"/C") ###

#
# Derived values
#
tree.Branch("UniversalTime"          ,ROOT.AddressOf(s,"UniversalTime"          ),"UniversalTime"          +"/l")
tree.Branch("WeekOfYear"             ,ROOT.AddressOf(s,"WeekOfYear"             ),"WeekOfYear"             +'/I') # First week of the year is short
tree.Branch("DayOfWeekFromMonday"    ,ROOT.AddressOf(s,"DayOfWeekFromMonday"    ),"DayOfWeekFromMonday"    +'/I') # From Monday, 4AM
tree.Branch("HourOfDayFromFourAM"    ,ROOT.AddressOf(s,"HourOfDayFromFourAM"    ),"HourOfDayFromFourAM"    +'/I')
tree.Branch("TimeOfDayFromFourAM"    ,ROOT.AddressOf(s,"TimeOfDayFromFourAM"    ),"TimeOfDayFromFourAM"    +'/F')

rootfile_all = TFile('output_all.root','RECREATE')
tree2 = ROOT.TTree("LongTerm","LongTerm")
s2 = ROOT.bgrootstruct()

tree2.Branch("UniversalTime"          ,ROOT.AddressOf(s2,"UniversalTime"          ),"UniversalTime"          +"/l")
tree2.Branch("BGReading"              ,ROOT.AddressOf(s2,"BGReading"              ),"BGReading"              +"/I")
tree2.Branch("WeekOfYear"             ,ROOT.AddressOf(s2,"WeekOfYear"             ),"WeekOfYear"             +'/I') # First week of the year is short
tree2.Branch("BWZCarbInput"           ,ROOT.AddressOf(s2,"BWZCarbInput"           ),"BWZCarbInput"           +"/I")
tree2.Branch("Rewind"                 ,ROOT.AddressOf(s2,"Rewind"                 ),"Rewind"                 +"/I") # Changed

import time
time_right_now = long(time.time())

def GetFromHistogram(hist,hour) :
    #print 'time of day from 4am is',hour
    # convert to bins - because these histograms go from 0 to 24.
    iterator = 0.
    while True :
        bin = hist.FindBin(hour-iterator)
        if bin == 0 :
            iterator -= 24
        result = hist.GetBinContent(bin)
        #print 'hour:',hour,'iterator:',iterator,'bin:',hist.FindBin(hour-iterator),'result:',result
        if result > 0 :
            return result
        iterator += 0.5

    return 0

for inputfilename in inputfilenames :

    inputfile = open(inputfilename,'r')
    counter = 0
    for line in inputfile:
        #print line
        counter += 1
        #print "counter is "+str(counter)
        #if counter > 100: 
        #  break
        linevector = line.split(',')
        if len(linevector)<20:
            continue

        for iter in range(len(linevector)):
            if len(linevector) == iter:
                break
            #
            # Condense everything in quotes into one line item.
            # Wow I was bad at coding.
            #
            if linevector[iter].find('\"') == 0:
                while True:
                    if linevector[iter+1].find('\"') > 0:
                        linevector[iter] = linevector[iter]+linevector[iter+1]
                        del linevector[iter+1]
                        break
                    linevector[iter] = linevector[iter]+linevector[iter+1]
                    del linevector[iter+1]
                #
            linevector[iter] = linevector[iter].translate(None,'\'\"\n')
            if linevector[iter] == '' and isNumber[iter]:
                linevector[iter] = -1
            #


        #
        # Collect basal information
        #
        if linevector[33] == 'ChangeBasalProfile' :
            this_basal = None
            for h_basal in basal_histograms :
                if linevector[3] in h_basal.GetName() :
                    this_basal = h_basal
            if not this_basal :
                basal_histograms.append(ROOT.TH1F('Basal '+linevector[3],linevector[3],48,0,24))
                basal_histograms[-1].SetDirectory(0)
                this_basal = basal_histograms[-1]
            # PATTERN_DATUM_ID=15906088830 PROFILE_INDEX=11 RATE=0.9 START_TIME=79200000
            start_time = int(2*int(linevector[34].split()[3].replace('START_TIME=',''))/3600000)
            start_time = start_time - 8 # half hour increments
            if start_time < 0 :
                start_time = start_time + 48 # half hour increments
            rate = float(linevector[34].split()[2].replace('RATE=',''))
            this_basal.SetBinContent(start_time+1,rate)

        #
        # Collect sensitivity information
        #
        if linevector[33] == 'ChangeInsulinSensitivity' :
            this_sensi = None
            for h_sensi in sensi_histograms :
                if linevector[3] in h_sensi.GetName() :
                    this_sensi = h_sensi
            if not this_sensi :
                sensi_histograms.append(ROOT.TH1F('Sensitivity '+linevector[3],linevector[3],48,0,24))
                sensi_histograms[-1].SetDirectory(0)
                this_sensi = sensi_histograms[-1]
            # PATTERN_DATUM_ID=15906088830 PROFILE_INDEX=11 RATE=0.9 START_TIME=79200000
            start_time = int(2*int(linevector[34].split()[3].replace('START_TIME=',''))/3600000)
            start_time = start_time - 8 # half hour increments
            if start_time < 0 :
                start_time = start_time + 48 # half hour increments
            rate = float(linevector[34].split()[2].replace('AMOUNT=',''))
            this_sensi.SetBinContent(start_time+1,rate)

        #
        # Collect insulin-carb ratios
        #
        if linevector[33] == 'ChangeCarbRatio' :
            this_ric = None
            for h_ric in ric_histograms :
                if linevector[3] in h_ric.GetName() :
                    this_ric = h_ric
            if not this_ric :
                ric_histograms.append(ROOT.TH1F('RIC '+linevector[3],linevector[3],48,0,24))
                ric_histograms[-1].SetDirectory(0)
                this_ric = ric_histograms[-1]
            # PATTERN_DATUM_ID=15906088830 PROFILE_INDEX=11 RATE=0.9 START_TIME=79200000
            start_time = int(2*int(linevector[34].split()[4].replace('START_TIME=',''))/3600000)
            start_time = start_time - 8 # half hour increments
            if start_time < 0 :
                start_time = start_time + 48 # half hour increments
            ric = float(linevector[34].split()[2].replace('AMOUNT=',''))
            this_ric.SetBinContent(start_time+1,ric)

        #
        # The standard data collection.
        #
        if len(linevector) == 39 and linevector[0] != "Index":
            s.Index = int(linevector[0])
            #print type(s.Index)
            s.Date                    = linevector[1]
            s.Time                    = linevector[2]
            s.Timestamp               = linevector[3]
            #s.UniversalTime           = long(time.mktime(time.strptime(linevector[3], "%m/%d/%y %H:%M:%S")))
            s.UniversalTime           = MyTime.TimeFromString(linevector[3])

            #
            # We take only the "BGReceived" BG data, to avoid double-counting.
            # linevector[5] = BGReading and linevector[6] = LinkedBGMeterID
            #
            if int(linevector[5]) > 0 and (not str(linevector[6])) :
                continue

            #
            # For JournalEntryMealMarker we enter that into the BWZEstimate entry.
            # The text field is linevector[33]
            if 'JournalEntryMealMarker' in linevector[33] :
                print 'JournalEntryMealMarker'
                linevector[23] = line.split('CARB_INPUT=')[1].split(',')[0]
                if not sensi_histograms :
                    print 'warning! No sensitivity on record!'
                elif not ric_histograms :
                    print 'warning! No insulin-carb ratio on record!'
                print 'time:',linevector[3]
                # carb ratio:
                linevector[21] = GetFromHistogram(ric_histograms[-1],MyTime.GetTimeOfDay(s.UniversalTime))
                # sensitivity:
                linevector[22] = GetFromHistogram(sensi_histograms[-1],MyTime.GetTimeOfDay(s.UniversalTime))

            #
            # For the Year-In-Review plot
            #
            s2.UniversalTime = MyTime.TimeFromString(linevector[3])
            s2.BGReading  = int(linevector[5])
            s2.WeekOfYear = MyTime.GetWeekOfYear(s.UniversalTime)
            s2.BWZCarbInput = int(linevector[23])
            s2.Rewind = 1 if linevector[17] else 0

            if s2.BGReading > 0 or s2.BWZFoodEstimate > 0 or s2.Rewind :
                tree2.Fill()

            print '%s %d \r'%(MyTime.StringFromTime(s.UniversalTime),MyTime.WeeksOld(s.UniversalTime)),
            if MyTime.WeeksOld(s.UniversalTime) > 4 :
                continue

            s.WeekOfYear              = MyTime.GetWeekOfYear(s.UniversalTime)
            s.DayOfWeekFromMonday     = MyTime.GetDayOfWeek(s.UniversalTime)
            s.HourOfDayFromFourAM     = MyTime.GetHourOfDay(s.UniversalTime)
            s.TimeOfDayFromFourAM     = float(MyTime.GetTimeOfDay(s.UniversalTime))
            #print s.TimeOfDayFromFourAM
            #
            #
            #
            s.NewDeviceTime           = linevector[4]
            s.BGReading               = int(linevector[5])
            #s.LinkedBGMeterID        = str(linevector[6])
            s.TempBasalAmount         = float(linevector[7])
            s.TempBasalType           = linevector[8]
            s.TempBasalDuration       = linevector[9]
            s.BolusType               = linevector[10]
            s.BolusVolumeSelected     = float(linevector[11])
            s.BolusVolumeDelivered    = float(linevector[12])
            s.ProgrammedBolusDuration = linevector[13]
            s.PrimeType               = linevector[14]
            s.PrimeVolumeDelivered    = float(linevector[15])
            s.Suspend                 = linevector[16]
            s.Rewind                  = 1 if linevector[17] else 0
            s.BWZEstimate             = float(linevector[18])
            s.BWZTargetHighBG         = int(linevector[19])
            s.BWZTargetLowBG          = int(linevector[20])
            s.BWZCarbRatio            = float(linevector[21])
            s.BWZInsulinSensitivity   = int(linevector[22])
            s.BWZCarbInput            = int(linevector[23])
            s.BWZBGInput              = int(linevector[24])
            s.BWZCorrectionEstimate   = float(linevector[25])
            s.BWZFoodEstimate         = float(linevector[26])
            s.BWZActiveInsulin        = float(linevector[27])
            s.Alarm                   = linevector[28]
            s.SensorCalibrationBG     = int(linevector[29])
            s.SensorGlucose           = int(linevector[30])
            s.ISIGValue               = float(linevector[31])
            s.DailyInsulinTotal       = float(linevector[32])
            s.RawType                 = linevector[33]
            s.RawValues               = linevector[34]
            s.RawID                   = long(linevector[35])
            s.RawUploadID             = long(linevector[36])
            s.RawSeqNum               = long(linevector[37])
            s.RawDeviceType           = linevector[38]

            tree.Fill()    

basal_histograms.reverse()
sensi_histograms.reverse()
ric_histograms.reverse()

for i in (basal_histograms + sensi_histograms + ric_histograms) :
    rootfile.cd()
    i.Write()
    rootfile_all.cd()
    i.Write()

rootfile.Write()
rootfile.Close()

rootfile_all.Write()
rootfile_all.Close()
