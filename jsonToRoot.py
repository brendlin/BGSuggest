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
        for br in dir(sDetailed) :
            if '__' in br :
                continue
            setattr(sDetailed,br,0)

        for j in line.keys() :
            if j in keys :
                continue
            keys.append(j)

        sDetailed.UniversalTime = MyTime.TimeFromString(line['deviceTime'])
        uTime = sDetailed.UniversalTime

        sDetailed.WeekOfYear              = MyTime.GetWeekOfYear(uTime)
        sDetailed.DayOfWeekFromMonday     = MyTime.GetDayOfWeek(uTime)
        sDetailed.HourOfDayFromFourAM     = MyTime.GetHourOfDay(uTime)
        sDetailed.TimeOfDayFromFourAM     = float(MyTime.GetTimeOfDay(uTime))

        type = line.get('type',None)
        if type not in ['cbg','smbg','basal','deviceEvent','bolus','wizard','pumpSettings'] :
            print type

        if line.get('type',None) == 'smbg' :
            conversion_factor = 1
            if line.get('units',None) == 'mmol/L' :
                conversion_factor = 18.01559
            sDetailed.BGReading = int( round(line.get('value') * conversion_factor) )

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
