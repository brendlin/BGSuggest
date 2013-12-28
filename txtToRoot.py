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
tree.Branch("Rewind"                 ,ROOT.AddressOf(s,"Rewind"                 ),"Rewind"                 +"/C") ###
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
        if len(linevector) == 39 and linevector[0] != "Index":
            s.Index = int(linevector[0])
            #print type(s.Index)
            s.Date                    = linevector[1]
            s.Time                    = linevector[2]
            s.Timestamp               = linevector[3]
            #s.UniversalTime           = long(time.mktime(time.strptime(linevector[3], "%m/%d/%y %H:%M:%S")))
            s.UniversalTime           = MyTime.TimeFromString(linevector[3])
            #
            #
            #
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
            s.Rewind                  = linevector[17]
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

rootfile.Write()
rootfile.Close()
