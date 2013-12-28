#!/usr/bin/env python
from ROOT import TF1,TH1F,gROOT
from PlotUtils import SmartPlot

import rootlogon
rootlogon.set_palette('Higgs')
gROOT.SetBatch(False)

aa= []

absorption = TF1('Insulin Absorption','1-(0.05)^((x/4.)^2) * (x<6)',0,6)
aa.append(absorption)

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

sp = SmartPlot(0,'','Insulin Absorption test',[dummy,integ,ddx]+aa,drawopt='l')
sp.plots[1].SetDrawOption('sames')
sp.plots[2].SetDrawOption('sames')

sp_prop = SmartPlot(0,'','Insulin Absorption',[absorption,absorption_rate],drawopt='l',canw=600,canh=450)
sp_prop.SetAxisLabels('Time (hours)','I/I_{0}')
sp_prop.plots[0].GetYaxis().SetRangeUser(0,1.3)
#sp_prop.DrawVertical(4)
#sp_prop.DrawHorizontal(0.95)
sp_prop.recreateLegend(.2,.7,.7,.86)

# sp.can.cd()
# b.Draw('sames')
# sp.leg.AddEntry('xx','Insulin Absorption Rate','pl')
# sp.leg.Draw()

#b.DrawIntegral("al sames")
#a.Draw("sames")
