import ROOT
import os
from TimeClass import MyTime
from Settings import SettingsHistograms
import time

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
    def formatCSVValue(self,strval) :
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
        if self.btype == 'Ftime' : # float, but need to divide by milliseconds
            return float(strval) / float(MyTime.MillisecondsInAnHour)
        return strval

    def AddBranchToTree(self,tree,addresses,name) :
        tmp_type = 'F' if (self.btype == 'Ftime') else self.btype
        tree.Branch(name,ROOT.AddressOf(addresses,name),'%s/%s'%(name,tmp_type))
        return

    def DefaultValue(self) :
        return {
            'I': -1,
            'O':  0,
            'L':  0,
            'F': -1,
            'Ftime':-1
            }.get(self.btype)

    def getFormattedValueFromVector(self,vector) :
        val = vector[self.csvIndex]
        return self.formatCSVValue(val)

def GetTreeBranchClassesDict() :
    import collections
    branches = collections.OrderedDict()
    branches['Index'                  ] = BRCL('I', 0) # number is the index
    branches['Date'                   ] = BRCL('C', 1)
    branches['Time'                   ] = BRCL('C', 2)
    branches['Timestamp'              ] = BRCL('C', 3)
    branches['NewDeviceTime'          ] = BRCL('C', 4)
    branches['BGReading'              ] = BRCL('I', 5) # ['value']
    branches['LinkedBGMeterID'        ] = BRCL('L', 6)
    branches['TempBasalAmount'        ] = BRCL('F', 7) # ['percent'] or ... ????
    branches['TempBasalType'          ] = BRCL('C', 8) # ['deliveryType']
    branches['TempBasalDuration'      ] = BRCL('Ftime', 9) # ['duration']
    branches['BolusType'              ] = BRCL('C',10)
    branches['BolusVolumeSelected'    ] = BRCL('F',11)
    branches['BolusVolumeDelivered'   ] = BRCL('F',12) # line[line['subType']]  ?????
    branches['ProgrammedBolusDuration'] = BRCL('Ftime',13)
    branches['PrimeType'              ] = BRCL('C',14)
    branches['PrimeVolumeDelivered'   ] = BRCL('F',15)
    branches['Suspend'                ] = BRCL('C',16)
    branches['Rewind'                 ] = BRCL('O',17) # 'deviceEvent' and 'reservoirChange'
    branches['BWZEstimate'            ] = BRCL('F',18) # net, probably ...
    branches['BWZTargetHighBG'        ] = BRCL('I',19) # ['bgTarget']['high']
    branches['BWZTargetLowBG'         ] = BRCL('I',20) # ['bgTarget']['low']
    branches['BWZCarbRatio'           ] = BRCL('F',21) # ['insulinCarbRatio']
    branches['BWZInsulinSensitivity'  ] = BRCL('I',22) # ['insulinSensitivity']
    branches['BWZCarbInput'           ] = BRCL('I',23) # ['carbInput']
    branches['BWZBGInput'             ] = BRCL('I',24) # ['bgInput']
    branches['BWZCorrectionEstimate'  ] = BRCL('F',25) # ['recommended']['correction']
    branches['BWZFoodEstimate'        ] = BRCL('F',26) # ['recommended']['carb']
    branches['BWZActiveInsulin'       ] = BRCL('F',27) # ??? 'net' ???
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

#
# This class is supposed to "manage the input".
# This means the files and trees are set up, and there is a function for getting the input files.
# Then you process a file by giving it both the file and the function used to process it.
# Obviously you need to know what ImportManager looks like to make a reasonable ProcessFile function,
# but this should put all of the "common" aspects of importing in once place.
#
class ImportManager :

    def __init__(self,options,args) :
        self.options = options
        self.init_time = time.mktime(time.localtime())

        ROOT.gROOT.LoadMacro('bgrootstruct.h+')

        self.rootfile = ROOT.TFile(options.outname,"RECREATE")
        self.treeDetailed = ROOT.TTree("DetailedResults","Detailed Results")
        self.sDetailed = ROOT.bgrootstruct()

        self.basal_histograms = SettingsHistograms('Basal')
        self.sensi_histograms = SettingsHistograms('Sensitivity')
        self.ric_histograms = SettingsHistograms('RIC')

        #
        # Add all of the (detailed) branches
        #
#         for br in branches.keys() :
#             self.treeDetailed.Branch(br,ROOT.AddressOf(self.sDetailed,br),'%s/%s'%(br,branches[br].btype))
        for br in branches.keys() :
            branches[br].AddBranchToTree(self.treeDetailed,self.sDetailed,br)

        #
        # Add Derived values to detailed tree
        #
        AddTimeBranchesToTree(self.treeDetailed,self.sDetailed)
        AddTimeCourtesyBranchesToTree(self.treeDetailed,self.sDetailed)

        #
        # Long-term data, which saves only a subset of the data.
        #
        self.sSummary = ROOT.bgrootstruct()

        if options.summary :
            self.rootfile_all = ROOT.TFile(options.outname.replace('.root','_LongTermSummary.root'),'RECREATE')
            self.treeSummary = ROOT.TTree("LongTermSummary","LongTermSummary")
            AddTimeBranchesToTree(self.treeSummary,self.sSummary)
            AddBasicBranchesToTree(self.treeSummary,self.sSummary)
        else :
            self.rootfile_all = None
            self.treeSummary = None

        return


    def GetInputFiles(self) :
        import re
        from string import ascii_letters

        inputfilenames = []
        for d in os.listdir(self.options.datadir) :
            # options.match_regexp should be a list of regexp tries
            # (e.g. ['CareLink_Export.*csv','Tidepool_Export.*json']
            matches = list( bool(re.match(matchstr,d)) for matchstr in self.options.match_regexp)
            if (True in matches) :
                inputfilenames.append('%s/%s'%(self.options.datadir,d))

        def cmp_mine(a, b):
            return cmp(a.lstrip(ascii_letters+'/_'),b.lstrip(ascii_letters+'/_'))

        inputfilenames = sorted(inputfilenames,cmp=cmp_mine)
        print inputfilenames
        return inputfilenames


    def ProcessFile(self,inputfilename,ProcessFileFunction) :
        ProcessFileFunction(inputfilename,self.treeDetailed,self.sDetailed,
                            self.treeSummary,self.sSummary,
                            self.basal_histograms,self.sensi_histograms,self.ric_histograms,
                            self.options)


    def Finish(self) :

        for settings_class in [self.basal_histograms,self.sensi_histograms,self.ric_histograms] :
            settings_class.WriteToFile(self.rootfile)
            settings_class.WriteToFile(self.rootfile_all)

        for f in [self.rootfile,self.rootfile_all] :
            if not f :
                continue

            f.Write()
            f.Close()

        print 'Time from init to finish: %2.2f'%(time.mktime(time.localtime()) - self.init_time)

        print
        return
