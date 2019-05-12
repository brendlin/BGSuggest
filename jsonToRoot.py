import ROOT
from ROOT import TFile
import sys
import time
from PyBGSuggestHelpers import TimeClass
import os
import json
import ImportHelpers

MyTime = TimeClass()

##
## This converts the json format of TidePool to root TTree format.
##

def main(options,args) :

    rootfilename = 'output_json.root'
    inputfilename = 'data/data_download.json'

    ROOT.gROOT.LoadMacro('bgrootstruct.h+')

    rootfile = TFile(rootfilename,"RECREATE")

    tree = ROOT.TTree("FullResults","Full Results")
    s = ROOT.bgrootstruct()

    basal_histograms = ImportHelpers.SettingsHistograms('Basal')
    sensi_histograms = ImportHelpers.SettingsHistograms('Sensitivity')
    ric_histograms = ImportHelpers.SettingsHistograms('RIC')

    branches = ImportHelpers.GetTreeBranchClassesDict()

    for br in branches.keys() :
        tree.Branch(br,ROOT.AddressOf(s,br),'%s/%s'%(br,branches[br].btype))

    #
    # Add Derived values to detailed tree
    #
    ImportHelpers.AddTimeBranchesToTree(tree,s)
    ImportHelpers.AddTimeCourtesyBranchesToTree(tree,s)

    import time
    time_right_now = long(time.time())

    keys = []
    json_file = open(inputfilename)

    data = json.load(json_file)
    for line in reversed(data) :

        if 'deviceTime' not in line.keys() :
            continue

        for j in line.keys() :
            if j in keys :
                continue
            keys.append(j)

        s.UniversalTime = MyTime.TimeFromString(line['deviceTime'])
        tree.Fill()

    print keys
    print

    for settings_class in [basal_histograms,sensi_histograms,ric_histograms] :
        settings_class.WriteToFile(rootfile)

    rootfile.Write()
    rootfile.Close()

    return

if __name__ == '__main__' :
    main(None,None)
