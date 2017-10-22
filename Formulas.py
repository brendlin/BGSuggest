#!/usr/bin/env python
import ROOT
from ROOT import TF1,TH1F,gROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc

# import rootlogon
# rootlogon.set_palette('Higgs')
gROOT.SetBatch(False)
plotfunc.SetupStyle()

aa= []

absorption = TF1('Insulin Absorption','1-(0.05)^((x/4.)^2) * (x<6)',0,6)
aa.append(absorption)

absorption_1 = TF1('Insulin Absorption','(0.05)^((x/2.)^2) * (x<9)',0,2.5)
absorption_2 = TF1('Insulin Absorption','(0.05)^((x/3.)^2) * (x<9)',0,3.5)
absorption_3 = TF1('Insulin Absorption','(0.05)^((x/4.)^2) * (x<9)',0,4.5)
absorption_4 = TF1('Insulin Absorption','(0.05)^((x/5.)^2) * (x<9)',0,5.5)
absorption_5 = TF1('Insulin Absorption','(0.05)^((x/6.)^2) * (x<9)',0,6.5)
absorption_6 = TF1('Insulin Absorption','(0.05)^((x/7.)^2) * (x<9)',0,7.5)
absorption_7 = TF1('Insulin Absorption','(0.05)^((x/8.)^2) * (x<9)',0,8.5)

absorption_1.SetTitle('2 Hour')
absorption_2.SetTitle('3 Hour')
absorption_3.SetTitle('4 Hour')
absorption_4.SetTitle('5 Hour')
absorption_5.SetTitle('6 Hour')
absorption_6.SetTitle('7 Hour')
absorption_7.SetTitle('8 Hour')

#
# derivative
#
absorption_rate = TF1('Insulin Absorption Rate','3.0*2*(1/4.)*(1/4.)*x*(0.05)^((x/4.)^2) * (x < 6)',0,6)
aa.append(absorption_rate)

import math

class BGFunction :
    def __init__(self) :
        self.iov_0 = 0 # universal time
        self.iov_1 = 6 # universal time
        self.const_BG = 0.
        self.S = 0 # sensitivity
        self.Ta = 4. # active insulin time
        self.I0 = 1.
        return

    def getDDXtimesInterval(self,time,delta) :
        #time += delta
        if time < self.iov_0 : return 0.
        if time > self.iov_1 : return 0.
        result = 2*math.pow((1/self.Ta),2)
        result *= 3.0 # ln 20
        result *= self.I0
        result *= time
        result *= math.pow(0.05,math.pow(time/self.Ta,2))
        #result *= (time < 6)
        result *= delta
        return result



#step = 0.25
step = 0.05

dummy = TH1F('asdf','asdf',6,0,6)

bg_func = BGFunction()
integ = TH1F('Integ','Integ',int(6/step),0,6)
ddx = TH1F('ddx','ddx',int(6/step),0,6)
bg = 0
for i in range(integ.GetNbinsX()) :
    time = i*step
    plus = bg_func.getDDXtimesInterval(time,step)
    bg+= plus
    integ.SetBinContent(i+1,bg)
    ddx.SetBinContent(i+1,plus)

sp = ROOT.TCanvas('Insulin Absorption test','Insulin Absorption test',600,500)
plotfunc.AddHistogram(sp,dummy,drawopt='l')
plotfunc.AddHistogram(sp,integ,drawopt='l')
plotfunc.AddHistogram(sp,ddx,drawopt='l')
for a in aa :
    plotfunc.AddHistogram(sp,a,drawopt='l')

sp_prop = ROOT.TCanvas('Insulin Absorption','Insulin Absorption',600,450)
plotfunc.AddHistogram(sp_prop,absorption,drawopt='l')
plotfunc.AddHistogram(sp_prop,absorption_rate,drawopt='l')
plotfunc.SetAxisLabels(sp_prop,'Time (hours)','I/I_{0}')
taxisfunc.SetYaxisRanges(sp_prop,0,1.3)


dummy = ROOT.TH1F('dummy','remove',10,-0.57,9.01)
dummy.GetYaxis().SetRangeUser(-0.05,1.015)
prop = ROOT.TCanvas('Insulin_Absorption','Insulin Absorption',781,545)
prop.SetLeftMargin(0.17/2.)
plotfunc.AddHistogram(prop,dummy)
image = ROOT.TASImage('plots/curve.png')
image.Draw('sames')
plotfunc.AddHistogram(prop,absorption_1,'lsames')
plotfunc.AddHistogram(prop,absorption_2,'lsames')
plotfunc.AddHistogram(prop,absorption_3,'lsames')
plotfunc.AddHistogram(prop,absorption_4,'lsames')
plotfunc.AddHistogram(prop,absorption_5,'lsames')
plotfunc.AddHistogram(prop,absorption_6,'lsames')
plotfunc.AddHistogram(prop,absorption_7,'lsames')
plotfunc.SetColors(prop)
plotfunc.SetAxisLabels(prop,'Time (hours)','% Insulin Remaining')
prop.GetPrimitive('Insulin_Absorption_dummy').GetYaxis().SetTitleOffset(0.9)
prop.GetPrimitive('Insulin_Absorption_dummy').GetXaxis().SetTitleOffset(1.1)
plotfunc.MakeLegend(prop,0.81,0.30,0.93,0.57)
prop.RedrawAxis()
prop.Modified()
prop.Update()

prop.Print('plots/%s.png'%(prop.GetName()))

#plotfunc.AutoFixAxes(prop)

# sp.can.cd()
# b.Draw('sames')
# sp.leg.AddEntry('xx','Insulin Absorption Rate','pl')
# sp.leg.Draw()

#b.DrawIntegral("al sames")
#a.Draw("sames")
