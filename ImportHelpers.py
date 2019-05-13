import ROOT

# BRanch CLass (for info on the tree branches)
class BRCL :
    btype = ''

    def __init__(self,_btype,_csvIndex=-1) :
        self.btype = _btype
        self.csvIndex = _csvIndex
        self.isNumber = (self.btype != 'C')
        return

    #
    # Figure out the correct format the the tree wants
    #
    def formatValue(self,strval) :
        if strval == '' and self.isNumber :
            return -1
        if self.btype == 'I' :
            return int(strval)
        if self.btype == 'O' :
            return 1 if strval else 0
        if self.btype == 'L' :
            return long(strval)
        if self.btype == 'F' :
            return float(strval)
        return strval

    def getFormattedValueFromVector(self,vector) :
        val = vector[self.csvIndex]
        return self.formatValue(val)

def GetTreeBranchClassesDict() :
    import collections
    branches = collections.OrderedDict()
    branches['Index'                  ] = BRCL('I',0) # number is the index
    branches['Date'                   ] = BRCL('C',1)
    branches['Time'                   ] = BRCL('C',2)
    branches['Timestamp'              ] = BRCL('C',3)
    branches['NewDeviceTime'          ] = BRCL('C',4)
    branches['BGReading'              ] = BRCL('I',5)
    branches['LinkedBGMeterID'        ] = BRCL('L',6)
    branches['TempBasalAmount'        ] = BRCL('F',7)
    branches['TempBasalType'          ] = BRCL('C',8)
    branches['TempBasalDuration'      ] = BRCL('C',9)
    branches['BolusType'              ] = BRCL('C',10)
    branches['BolusVolumeSelected'    ] = BRCL('F',11)
    branches['BolusVolumeDelivered'   ] = BRCL('F',12)
    branches['ProgrammedBolusDuration'] = BRCL('C',13)
    branches['PrimeType'              ] = BRCL('C',14)
    branches['PrimeVolumeDelivered'   ] = BRCL('F',15)
    branches['Suspend'                ] = BRCL('C',16)
    branches['Rewind'                 ] = BRCL('O',17)
    branches['BWZEstimate'            ] = BRCL('F',18)
    branches['BWZTargetHighBG'        ] = BRCL('I',19)
    branches['BWZTargetLowBG'         ] = BRCL('I',20)
    branches['BWZCarbRatio'           ] = BRCL('F',21)
    branches['BWZInsulinSensitivity'  ] = BRCL('I',22)
    branches['BWZCarbInput'           ] = BRCL('I',23)
    branches['BWZBGInput'             ] = BRCL('I',24)
    branches['BWZCorrectionEstimate'  ] = BRCL('F',25)
    branches['BWZFoodEstimate'        ] = BRCL('F',26)
    branches['BWZActiveInsulin'       ] = BRCL('F',27)
    branches['Alarm'                  ] = BRCL('C',28)
    branches['SensorCalibrationBG'    ] = BRCL('I',29)
    branches['SensorGlucose'          ] = BRCL('I',30)
    branches['ISIGValue'              ] = BRCL('F',31)
    branches['DailyInsulinTotal'      ] = BRCL('F',32)
    branches['RawType'                ] = BRCL('C',33)
    branches['RawValues'              ] = BRCL('C',34)
    branches['RawID'                  ] = BRCL('L',35)
    branches['RawUploadID'            ] = BRCL('L',36)
    branches['RawSeqNum'              ] = BRCL('L',37)
    branches['RawDeviceType'          ] = BRCL('C',38)
    return branches

# Do not worry - if you import this file multiple times, you will not create multiple instances.
# The module will be loaded once, and each subsequent "import" will just link the file to
# the static state of the first-imported file.
branches = GetTreeBranchClassesDict()

def AddTimeBranchesToTree(tree,addresses) :
    tree.Branch("UniversalTime"          ,ROOT.AddressOf(addresses,"UniversalTime"          ),"UniversalTime"          +"/l")
    tree.Branch("WeekOfYear"             ,ROOT.AddressOf(addresses,"WeekOfYear"             ),"WeekOfYear"             +'/I') # First week of the year is short
    return

def AddTimeCourtesyBranchesToTree(tree,addresses) :
    tree.Branch("DayOfWeekFromMonday"    ,ROOT.AddressOf(addresses,"DayOfWeekFromMonday"    ),"DayOfWeekFromMonday"    +'/I') # From Monday, 4AM
    tree.Branch("HourOfDayFromFourAM"    ,ROOT.AddressOf(addresses,"HourOfDayFromFourAM"    ),"HourOfDayFromFourAM"    +'/I')
    tree.Branch("TimeOfDayFromFourAM"    ,ROOT.AddressOf(addresses,"TimeOfDayFromFourAM"    ),"TimeOfDayFromFourAM"    +'/F')
    return

def AddBasicBranchesToTree(tree,addresses) :
    tree.Branch("BGReading"              ,ROOT.AddressOf(addresses,"BGReading"              ),"BGReading"              +"/I")
    tree.Branch("BWZCarbInput"           ,ROOT.AddressOf(addresses,"BWZCarbInput"           ),"BWZCarbInput"           +"/I")
    tree.Branch("Rewind"                 ,ROOT.AddressOf(addresses,"Rewind"                 ),"Rewind"                 +"/I") # Changed
    tree.Branch("RecentSensorISIG"       ,ROOT.AddressOf(addresses,"RecentSensorISIG"       ),"RecentSensorISIG"       +"/F")
    tree.Branch("MARD"                   ,ROOT.AddressOf(addresses,"MARD"                   ),"MARD"                   +"/F")
    tree.Branch("SensorAgeDays"          ,ROOT.AddressOf(addresses,"SensorAgeDays"          ),"SensorAgeDays"          +"/F")


class CrossDatumDataStorage :
    current_sensor_age_utc = -1
    last_sensor_isig_age = -1
    last_sensor_isig = -1
    last_sensor_bg = -1

dataStorageInstance = CrossDatumDataStorage()

class SettingsHistograms :

    def __init__(self,_type_of_hist) :
        self.hist_list = []
        self.type_of_hist = _type_of_hist
        return

    def latestHistogram(self) :
        if not self.hist_list :
            print 'warning! No insulin-carb ratio on record!'
        else :
            return self.hist_list[-1]

        return None

    def getOrMakeHistogram(self,histo_tag) :

        # Get the latest histogram, if it exists
        for hist in self.hist_list :
            if histo_tag in hist.GetName() :
                return hist

        # If it does not exist, make a new one:
        # They are all half-hour increments, starting from 4am!
        hist = ROOT.TH1F('%s %s'%(self.type_of_hist,histo_tag),histo_tag,48,0,24)
        hist.SetDirectory(0)

        # append the new histogram to the list
        self.hist_list.append(hist)

        return hist

    def WriteToFile(self,rootfile) :
        for i in reversed(self.hist_list) :
            rootfile.cd()
            i.Write()
        return

    def AddSettingToHistogram(self,histo_tag,timeOfDay_midnight,value) :
        # The input, timeOfDay, is in hours (float), starting from MIDNIGHT
        # but it will be CONVERTED to 4am

        hist = self.getOrMakeHistogram(histo_tag)

        # half hour increments, 12am to 4am start time conversion:
        timeOfDay_midnight = int(timeOfDay_midnight)
        timeOfDay = timeOfDay_midnight - 8 

        # Roll pre-4am to the end of the histogram.
        if timeOfDay < 0 :
            timeOfDay = timeOfDay + 48 # half hour increments

        hist.SetBinContent(timeOfDay+1,value)
        return


    def GetSettingFromHistogram(self,timeOfDay) :
        # The input, timeOfDay, is in hours (float), starting from 4am
        # convert to bins - because these histograms go from 0 to 24.

        hist = self.latestHistogram()

        if not hist :
            'Missing histogram - exiting.'
            import sys; sys.exit;

        iterator = 0.
        while True :
            bin = hist.FindBin(timeOfDay-iterator)
            if bin == 0 :
                iterator -= 24

            # Both the input and the histogram start from 4am.
            result = hist.GetBinContent(bin)
            #print 'timeOfDay:',timeOfDay,'iterator:',iterator,'bin:',hist.FindBin(timeOfDay-iterator),'result:',result

            # Return a non-zero result.
            if result > 0 :
                return result

            # If a result is zero, look back another half hour...
            iterator += 0.5

        return 0

#
# This function is meant to run the whole job basically.
# The setup is done here, and then you plug in the specific function you want to run over.
#
def mainImportFunction(options,args,ProcessFileFunction) :
    import os
    import re
    from string import ascii_letters

    inputfilenames = []
    for d in os.listdir(options.datadir) :
        # options.match_regexp should be a list of regexp tries
        # (e.g. ['CareLink_Export.*csv','Tidepool_Export.*json']
        matches = list( bool(re.match(matchstr,d)) for matchstr in options.match_regexp)
        if (True in matches) :
            inputfilenames.append('%s/%s'%(options.datadir,d))

    def cmp_mine(a, b):
        return cmp(a.lstrip(ascii_letters+'/_'),b.lstrip(ascii_letters+'/_'))

    inputfilenames = sorted(inputfilenames,cmp=cmp_mine)
    print inputfilenames

    ROOT.gROOT.LoadMacro('bgrootstruct.h+')

    rootfile = ROOT.TFile(options.outname,"RECREATE")

    treeDetailed = ROOT.TTree("DetailedResults","Detailed Results")
    sDetailed = ROOT.bgrootstruct()

    basal_histograms = SettingsHistograms('Basal')
    sensi_histograms = SettingsHistograms('Sensitivity')
    ric_histograms = SettingsHistograms('RIC')

    #
    # Add all of the (detailed) branches
    #
    for br in branches.keys() :
        treeDetailed.Branch(br,ROOT.AddressOf(sDetailed,br),'%s/%s'%(br,branches[br].btype))

    #
    # Add Derived values to detailed tree
    #
    AddTimeBranchesToTree(treeDetailed,sDetailed)
    AddTimeCourtesyBranchesToTree(treeDetailed,sDetailed)

    #
    # Long-term data, which saves only a subset of the data.
    #
    rootfile_all = ROOT.TFile(options.outname.replace('.root','_LongTermSummary.root'),'RECREATE')
    treeSummary = ROOT.TTree("LongTermSummary","LongTermSummary")
    sSummary = ROOT.bgrootstruct()

    AddTimeBranchesToTree(treeSummary,sSummary)
    AddBasicBranchesToTree(treeSummary,sSummary)

    for inputfilename in inputfilenames :
        ProcessFileFunction(inputfilename,treeDetailed,sDetailed,
                            treeSummary,sSummary,
                            basal_histograms,sensi_histograms,ric_histograms,
                            options)

    for settings_class in [basal_histograms,sensi_histograms,ric_histograms] :
        settings_class.WriteToFile(rootfile)
        settings_class.WriteToFile(rootfile_all)

    for f in [rootfile,rootfile_all] :
        f.Write()
        f.Close()

    print
    return
