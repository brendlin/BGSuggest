import ROOT
from array import array
import PlotFunctions as plotfunc

def IsigStudy(tree) :

    study = ROOT.TCanvas('study','study',500,500)

    req = 'BGReading > 00 && MARD > -99 && RecentSensorISIG>0'
#     n = tree.Draw('fabs(MARD):SensorAgeDays>>hist%d(100,0,.5,100,0,60)',req,'goff')
#     n = tree.Draw('RecentSensorISIG:SensorAgeDays>>hist%d(100,0,100,100,0,6)',req,'goff')
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     n = tree.Draw('RecentSensorISIG/BGReading:SensorAgeDays>>hist%d(100,0,1,100,0,6)',req,'goff')
#     if not n : return study
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)

    #hist = ROOT.TH1F('hist','hist',100,-2,2)
    req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0'
    n = tree.Draw('MARD>>hist(25,-1,1)',req,'goff')
    print 'n=',n
    hist = ROOT.gDirectory.Get('hist')
    hist.Sumw2()
    hist.Scale(1/float(hist.Integral(0,hist.GetNbinsX()+1)))
    plotfunc.AddHistogram(study,hist)
#     for i in range(10) :
#         req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && %d <= SensorAgeDays && SensorAgeDays < %d'%(i,i+1)
#         n = tree.Draw('MARD>>hist(25,-1,1)',req,'goff')
#         hist = ROOT.gDirectory.Get('hist')
#         hist.Sumw2()
#         hist.Scale(1/float(hist.Integral(0,hist.GetNbinsX()+1)))
#         plotfunc.AddHistogram(study,hist)


#     h = ROOT.TH1F('hist','hist',10,0,10)

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 0 <= SensorAgeDays && SensorAgeDays < 1'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(1,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 1 <= SensorAgeDays && SensorAgeDays < 2'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(2,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 2 <= SensorAgeDays && SensorAgeDays < 3'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(3,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 3 <= SensorAgeDays && SensorAgeDays < 4'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(4,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 4 <= SensorAgeDays && SensorAgeDays < 5'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(5,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 5 <= SensorAgeDays && SensorAgeDays < 6'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(6,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 6 <= SensorAgeDays && SensorAgeDays < 7'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(7,x/float(n))

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 7 <= SensorAgeDays'
#     n = tree.Draw('fabs(MARD)>>hist%d(100,0,6)',req,'goff')
#     x = 0
#     for i in range(n) :
#         x += tree.GetV1()[i]
#     h.SetBinContent(8,x/float(n))

#     plotfunc.AddHistogram(study,h)

#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 0 <= SensorAgeDays && SensorAgeDays < 1'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)
    
#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 1 <= SensorAgeDays && SensorAgeDays < 2'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)
    
#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 2 <= SensorAgeDays && SensorAgeDays < 3'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)
    
#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 3 <= SensorAgeDays && SensorAgeDays < 4'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)
    
#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 4 <= SensorAgeDays && SensorAgeDays < 5'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)
    
#     req = 'BGReading>00 && MARD>-99 && RecentSensorISIG>0 && 5 <= SensorAgeDays && SensorAgeDays < 6'
#     n = tree.Draw('RecentSensorISIG:BGReading>>hist%d(100,0,1,100,0,6)',req,'goff')
#     graph = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
#     plotfunc.AddHistogram(study,graph)

    plotfunc.SetColors(study)
    plotfunc.MakeLegend(study)

    return study
