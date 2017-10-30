import ROOT
from array import array
from PyBGSuggestHelpers import TimeClass,GetHistWithTimeAxis
t = TimeClass()
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc

# Weeks (inclusive)
def GetOverview(tree,d1,d2) :
    print 'Getting overview from week %d to week %d'%(d1,d2)

    hist = GetHistWithTimeAxis()
    last_week = 0

    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        last_week = max(last_week,tree.WeekOfYear)

    print 'Last week: %d'%(last_week)
    graphs = []
    hists_fine = []
    hists_coarse = []
    print 'Getting overview from week %d to week %d'%(last_week-d1,last_week-d2)
    req = 'BGReading > 0 && %d <= WeekOfYear && WeekOfYear <= %d'%(last_week-d1,last_week-d2)
    n = tree.Draw('BGReading:TimeOfDayFromFourAM>>hist%d%d(50,-0.5,24.5,41,40,450)'%(last_week-d1,last_week-d2),req,'goff')
    if not n : 
        print 'Error: no readings found.'
        return None
    graphs.append(ROOT.TGraph(n,tree.GetV2(),tree.GetV1()))

    Avg = 0
    n_below_80  = 0
    n_target    = 0
    n_above_160 = 0
    n_above_200 = 0
    for x in range(n) :
        num = tree.GetV1()[x]
        Avg += num
        if (num > 160 )    : n_above_160 += 1
        elif (num < 80)    : n_below_80  += 1
        else               : n_target    += 1
        if (num >= 200)    : n_above_200 += 1
    Avg = Avg / float(n)
    n_below_80  = 100.*n_below_80 /float(n)
    n_target    = 100.*n_target   /float(n)
    n_above_160 = 100.*n_above_160/float(n)
    n_above_200 = 100.*n_above_200/float(n)

    time_bins = [-0.5,3,7,9,12,16,20,24.5]
    # fine_bins = list(-0.5+i for i in range(26))
    ltime = len(time_bins[:-1])
    bg_bins = [40,80,120,160,200,300,450]
    lbg = len(bg_bins[:-1])

    hists_fine.append(ROOT.gDirectory.Get('hist%d%d'%(last_week-d1,last_week-d2)))
    key = 'coarse hist %d %d'%(last_week-d1,last_week-d2)
    hists_coarse.append(ROOT.TH2F(key,key,ltime,array('d',time_bins),lbg,array('d',bg_bins)))

    smallest_bin = 0
    for j in range(hists_fine[-1].GetNbinsX()) :
        c_x = list(hists_fine[-1].GetXaxis().GetBinLowEdge(j+1) < a for a in time_bins).index(True)
        for k in range(hists_fine[-1].GetNbinsY()) :
            c_y = list(hists_fine[-1].GetYaxis().GetBinLowEdge(k+1) < a for a in bg_bins).index(True)
            val = hists_fine[-1].GetBinContent(j+1,k+1)
            if val : 
                hists_coarse[-1].SetBinContent(c_x,c_y,val+hists_coarse[-1].GetBinContent(c_x,c_y))

    nametitle = 'Week %d (N=%d)'%(last_week-d1,graphs[-1].GetN())
    graphs[-1].SetNameTitle(nametitle,nametitle)

    title = '%s (N=%d, #mu=%0.1f).'%(t.GetWeeksString(last_week-d1,last_week-d2),graphs[-1].GetN(),Avg)
    text_l2 = '%2.1f%% below, %2.1f%% target, %2.1f%% above'%(n_below_80,n_target,n_above_160)
    text_l3 = '%2.1f%% above 200'%(n_above_200)

    can = ROOT.TCanvas('year_in_review','year in review',600,500)
    plotfunc.SetColorGradient('HiggsBlue')
    hist.GetXaxis().SetLabelOffset(0.007)
    plotfunc.AddHistogram(can,hist)
    taxisfunc.SetYaxisRanges(can,40,450)
    plotfunc.AddHistogram(can,hists_coarse[-1],drawopt='colz')
    plotfunc.AddHistogram(can,graphs[-1])
    plotfunc.SetRightMargin(can,.15)
    plotfunc.SetAxisLabels(can,'','BG Reading')
    plotfunc.DrawText(can,[title,text_l2,text_l3],0.19,0.79,0.73,0.92)
    can.Modified()
    can.Update()

    return can
