#!/usr/bin/env python
from ROOT import TFile,TGraph,TCanvas,gROOT,gDirectory,TH1F,TH2F,TF1,kGray,kBlack,gStyle,TGraphAsymmErrors
from PlotUtils import SmartPlot,color,markerstyles
from array import array
from PyBGSuggestHelpers import TimeClass
t = TimeClass()
import rootlogon
rootlogon.set_palette('Higgs')
gStyle.SetCanvasDefW(800)
gStyle.SetCanvasDefH(500)
import time
import math

NWEEKS = 104

ADA = False
KURT = True

gROOT.SetBatch(False)

f = TFile('output.root')
e = f.Get('Tree Name')

last_week = 0

for i in range(e.GetEntries()) :
    e.GetEntry(i)
    last_week = max(last_week,e.WeekOfYear)

time_bins = [-0.5,3,7,9,12,16,20,24.5]
#fine_bins = list(-0.5+i for i in range(26))
ltime = len(time_bins[:-1])
bg_bins = [40,80,120,160,200,300,450]
food_bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140]
lbg = len(bg_bins[:-1])
lf = len(food_bins[:-1])

daytitles = {0:'Monday'
            ,1:'Tuesday'
            ,2:'Wednesday'
            ,3:'Thursday'
            ,4:'Friday'
            ,5:'Saturday'
            ,6:'Sunday'} 

daynumbers ={'Monday'   :0
            ,'Tuesday'  :1
            ,'Wednesday':2
            ,'Thursday' :3
            ,'Friday'   :4
            ,'Saturday' :5
            ,'Sunday'   :6} 

hist= TH1F('Dummy','Dummy',25,-0.5,24.5)
hist.GetXaxis().SetBinLabel(1,'4 am')
hist.GetXaxis().SetBinLabel(5,'8 am')
hist.GetXaxis().SetBinLabel(9,'12 pm')
hist.GetXaxis().SetBinLabel(13,'4 pm')
hist.GetXaxis().SetBinLabel(17,'8 pm')
hist.GetXaxis().SetBinLabel(21,'12 am')
hist.GetXaxis().SetLabelFont(42)
hist.GetYaxis().SetLabelFont(42)

fhist = hist.Clone()
fhist.SetNameTitle('FDummy','FDummy')

f1hist = hist.Clone()
f1hist.SetNameTitle('F1Dummy','F1Dummy')

print 'c = WeekPlot()'

def GetIntegratedAverage(graph) :
    tot = 0
    n = 0
    for i in range(graph.GetN()) :
        if graph.GetY()[i] :
            tot += graph.GetY()[i]
            n += 1
    return tot/float(n)


def RootMeanSquare(vals) :
    avg = sum(vals)/float(len(vals))
    return math.sqrt(sum(list(math.pow(a-avg,2) for a in vals))/float(len(vals)))


class WeekPlot :

    def __init__(self) :
        self.plain_hist = None
        self.main_hist = None

        self.old_plain_hists = []
        self.old_main_hists = []

        self.RIC_fac_up = 1.0 #0.9
        self.RIC_fac_dn = 1.0 #1.1

        self.RIC_n_up = -1.
        self.RIC_n_dn =  1.

        self.S_fac_up = 1.1
        self.S_fac_dn = 0.9

        self.C_fac_up = 1.1
        self.C_fac_dn = 0.9

        print 'Options:'
        print '   c.Detailed(\'last\')'
        print '   c.GetDetailed(18)'
        print '   c.m()'
        print '   c.Overview(\'last\')'
        print '   c.GetOverview(18,18)'
        print '   c.YearInReview()'
        print '   c.SuppliesSummary()'
        print '   c.DoSample()'

        return

    def SuppliesSummary(self) :
        rewind_histo   = TH1F('Rewind Frequency','Rewind Frequency',48,0,6)
        supplies_histo = TH1F('Infusion Sets','Infusion Sets',NWEEKS,0,NWEEKS)
        strips_histo   = TH1F('Test Strips /10','Test Strips /10',NWEEKS,0,NWEEKS)
        insulin_histo  = TH1F('Insulin (mL, 10mL/vial)','Insulin (mL, 10mL/vial)',NWEEKS,0,NWEEKS)
        test_f_histo   = TH1F('Test Frequency','Test Frequency',96,0,24)
        last_rewind     = 0
        last_bg         = 0
        rolling_rewinds = 0
        rolling_bgs     = 0
        first_week      = 0
        rolling_insulin = 0
        last_insulin    = 0
        week_in_question = first_week
        for i in range(e.GetEntries()) :
            e.GetEntry(i)
            if e.WeekOfYear < first_week : continue
            if e.WeekOfYear != week_in_question :
                if week_in_question ==  0 : 
                    rolling_rewinds += 32
                    rolling_bgs     += 1000./10.
                    rolling_insulin += 90.
                if week_in_question == 19 : 
                    rolling_rewinds += 50
                    rolling_bgs     += 400./10.
                    rolling_insulin += 50.
                if week_in_question == 47 : 
                    rolling_rewinds += 10
                    rolling_bgs     += 100./10.
                if week_in_question == 49 : 
                    rolling_rewinds += 50
                    rolling_bgs     += 450./10.
                if week_in_question == 50 :
                    rolling_insulin = 90.
                supplies_histo.SetBinContent(week_in_question+1,rolling_rewinds)
                strips_histo.SetBinContent(week_in_question+1,rolling_bgs)
                insulin_histo.SetBinContent(week_in_question+1,rolling_insulin)
                week_in_question = e.WeekOfYear
                #
                rolling_insulin = rolling_insulin - 2.5

            if e.Rewind :
                rolling_rewinds -= 1
                if last_rewind :
                    rewind_histo.Fill((e.UniversalTime-last_rewind)/float(t.OneDay))
                last_rewind = e.UniversalTime
            if e.BGReading > 0. :
                rolling_bgs -= 1/10.
                if last_bg :
                    test_f_histo.Fill((e.UniversalTime-last_bg)/float(t.OneHour))
                last_bg = e.UniversalTime

        print week_in_question
        supplies_histo.SetBinContent(week_in_question+1,rolling_rewinds)
        strips_histo.SetBinContent(week_in_question+1,rolling_bgs)
        insulin_histo.SetBinContent(week_in_question+1,rolling_insulin)

        self.rewind_plot = SmartPlot(0,'','Rewind Frequency',[rewind_histo],drawopt='hist')
        self.rewind_plot.SetAxisLabels('Days between Rewinds','Entries')
        test_f_histo.SetName('Test Frequency (avg=%2.2f/day)'%(24./float(test_f_histo.GetMean())))
        self.test_f_plot = SmartPlot(0,'','Test Frequency',[test_f_histo],drawopt='hist')
        self.test_f_plot.SetAxisLabels('Hours between tests','Entries')
        self.supplies_plot = SmartPlot(0,'','Supplies Plot',[supplies_histo,strips_histo,insulin_histo],drawopt='hist')
        self.supplies_plot.SetAxisLabels('Week Of Year','# of supplies')
        from ROOT import kRed,kAzure
        self.supplies_plot.plots[0].GetYaxis().SetRangeUser(0,120)
        self.supplies_plot.DrawHorizontal(30./3.,style=2)
        self.supplies_plot.DrawHorizontal(4.5*30./10.,style=2,color=kRed+1)
        self.supplies_plot.DrawTextNDC(.2,.135,'30 Days Left')
        self.supplies_plot.DrawTextNDC(.2,.20,'30 Days Left',color=kRed+1)
        self.supplies_plot.DrawTextNDC(.2,.235,'100 u/mL, 1000 u/vial',color=kAzure-2)

    def a1cToBS(self,n) :
        if ADA :
            return 28.71*(n-7)+154.42,'28.71*(n-7)+154.42'
        elif KURT :
            return 45.00*(n-7)+149.00,'45.00*(n-7)+149.00'
        return 35.6*(n-7)+171.90,'35.6*(n-7)+171.90'

    def YearInReview(self) :
        yir = TH1F('AverageBG','AverageBG',NWEEKS,0,NWEEKS)
        for i in range(last_week+1) :
            req = 'BGReading > 00 && WeekOfYear == %d'%(i)
            n = e.Draw('BGReading>>hist%d(100,0,500)'%(i),req,'goff')
            if not n : continue
            Avg = 0
            vals = []
            for x in range(n) :
                Avg += e.GetV1()[x]
                vals.append(e.GetV1()[x])
            Avg = Avg / float(n)

            yir.SetBinContent(i+1,Avg)
            yir.SetBinError(i+1,RootMeanSquare(vals))

        yir_smooth = TH1F('4-week average','4-week average',NWEEKS,0,NWEEKS)
        for i in range(last_week+1) :
            req = 'BGReading > 00 && WeekOfYear <= %d && WeekOfYear >= %d-3'%(i,i)
            n = e.Draw('BGReading>>hist%d(100,-500,500)'%(i),req,'goff')
            if not n : continue
            Avg = 0
            vals = []
            for x in range(n) :
                Avg += e.GetV1()[x]
                vals.append(e.GetV1()[x])
            Avg = Avg / float(n)

            yir_smooth.SetBinContent(i+1,Avg)
            yir_smooth.SetBinError(i+1,RootMeanSquare(vals))

        yir_17w = TH1F('17-week average','17-week average',NWEEKS,0,NWEEKS)
        for i in range(last_week+1) :
            req = 'BGReading > 00 && WeekOfYear <= %d && WeekOfYear >= %d-16'%(i,i)
            n = e.Draw('BGReading>>hist%d(100,-500,500)'%(i),req,'goff')
            if not n : continue
            Avg = 0
            vals = []
            for x in range(n) :
                Avg += e.GetV1()[x]
                vals.append(e.GetV1()[x])
            Avg = Avg / float(n)

            yir_17w.SetBinContent(i+1,Avg)
            yir_17w.SetBinError(i+1,RootMeanSquare(vals))
               
        yir_food = TH1F('Food Intake','Food Intake',NWEEKS,0,NWEEKS)
        for i in range(last_week+1) :
            req = 'BWZCarbInput > 00 && WeekOfYear == %d'%(i)
            n = e.Draw('BWZCarbInput>>hist%d(100,-500,500)'%(i),req,'goff')
            if not n : continue
            Tot = 0
            for x in range(n) :
                Tot += e.GetV1()[x]
            yir_food.SetBinContent(i+1,Tot/10.)
               
        a1x = []
        a1y = []
        # january
        a1x.append(t.GetWeekOfYear(t.TimeFromString('01/12/13 04:00:00')))
        a1y.append(self.a1cToBS(7.9)[0])
        # april
        a1x.append(t.GetWeekOfYear(t.TimeFromString('04/13/13 04:00:00')))
        a1y.append(self.a1cToBS(8.0)[0])
        # august
        a1x.append(t.GetWeekOfYear(t.TimeFromString('08/19/13 04:00:00')))
        a1y.append(self.a1cToBS(7.7)[0])
        # december
        a1x.append(t.GetWeekOfYear(t.TimeFromString('12/19/13 04:00:00')))
        a1y.append(self.a1cToBS(7.6)[0])
        #
        x_a1 = array('d',a1x)
        y_a1 = array('d',a1y)
        a1cs = TGraph(len(x_a1),x_a1,y_a1)
        a1csname = 'a1c, %s'%(self.a1cToBS(0.)[1])
        a1cs.SetNameTitle(a1csname,a1csname)
        from ROOT import kAzure
        a1cs.SetMarkerColor(kAzure-2)
        a1cs.SetMarkerStyle(20)
        a1cs.SetMarkerSize(2)

        dummy2 = TH1F('dummy2','dummy2',12*NWEEKS/52,0,NWEEKS)
        dummy2.GetXaxis().SetBinLabel( 1,'Jan')
        dummy2.GetXaxis().SetBinLabel( 2,'Feb')
        dummy2.GetXaxis().SetBinLabel( 3,'Mar')
        dummy2.GetXaxis().SetBinLabel( 4,'Apr')
        dummy2.GetXaxis().SetBinLabel( 5,'May')
        dummy2.GetXaxis().SetBinLabel( 6,'Jun')
        dummy2.GetXaxis().SetBinLabel( 7,'Jul')
        dummy2.GetXaxis().SetBinLabel( 8,'Aug')
        dummy2.GetXaxis().SetBinLabel( 9,'Sep')
        dummy2.GetXaxis().SetBinLabel(10,'Oct')
        dummy2.GetXaxis().SetBinLabel(11,'Nov')
        dummy2.GetXaxis().SetBinLabel(12,'Dec')

        self.year_in_review = SmartPlot(0,'','Year In Review',[dummy2,yir,yir_smooth,yir_17w,yir_food],canw=1000)
        from ROOT import kRed,kAzure,kBlack
        self.year_in_review.SetColors(these_colors=[kBlack,kBlack,kRed+1,kAzure-2,kBlack])
        self.year_in_review.plots[0].SetLineWidth(1)
        self.year_in_review.plots[0].GetYaxis().SetRangeUser(50,300)
        highlight = 3
        highlight_c = kBlack
        self.year_in_review.plots[highlight].SetDrawOption('pE3sames')
        self.year_in_review.plots[4].SetDrawOption('histsames')
        self.year_in_review.plots[highlight].SetFillStyle(3001)
        self.year_in_review.plots[highlight].SetFillColor(1)
        self.year_in_review.plots[highlight].SetFillColor(highlight_c)
        self.year_in_review.plots[highlight].Draw('samesE1')
        self.year_in_review.plots.append(a1cs)
        self.year_in_review.plots[-1].Draw('p')
        self.year_in_review.SetAxisLabels('week of year','avg BS mg/dL')
        if ADA :
            self.year_in_review.DrawHorizontal(126.0)
            self.year_in_review.DrawHorizontal(154.0)
            self.year_in_review.DrawHorizontal(183.0)
        elif KURT :
            self.year_in_review.DrawHorizontal(self.a1cToBS(6.)[0])
            self.year_in_review.DrawHorizontal(self.a1cToBS(7.)[0])
            self.year_in_review.DrawHorizontal(self.a1cToBS(8.)[0])
        else :
            self.year_in_review.DrawHorizontal(136.3)
            self.year_in_review.DrawHorizontal(171.9)
            self.year_in_review.DrawHorizontal(207.5)
        self.year_in_review.recreateLegend(.2,.15,.7,.25)
        self.year_in_review.can.SetGrid()

    def TurnOffDays(self) :
        a = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        a1 = list(aa +' prediction' for aa in a)
        a2 = list(aa +' food' for aa in a)
        a += a1
        a += a2

        for i in a :
            if self.main_hist.can.GetPrimitive(i) :
                #self.main_hist.can.GetPrimitive(i).SetDrawOption('E3')
                #self.main_hist.can.GetPrimitive(i).SetMarkerSize(0)
                #self.main_hist.can.GetPrimitive(i).SetLineWidth(0)
                #self.main_hist.can.GetPrimitive(i).SetMarkerColor(0)
                #self.main_hist.can.GetPrimitive(i).SetFillColor(0)
                h = self.main_hist.can.GetPrimitive(i)
                self.main_hist.can.GetListOfPrimitives().Remove(h)
        self.main_hist.can.Draw()

        return

    def SetGraphs(self,a=[]) :
        if not a : a = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        if self.main_hist.ngraphs < 7 :
            a = a[:self.main_hist.ngraphs]

        icol   = []
        iregs  = []
        ipreds = []
        ifoods = []
        for i in a :
            icol.append(daynumbers[i])
            iregs.append(2+daynumbers[i])
            ipreds.append(2+daynumbers[i]+self.main_hist.ngraphs)
            ifoods.append(2+daynumbers[i]+2*self.main_hist.ngraphs)

        print iregs
        print ipreds
        print ifoods

        self.main_hist.can.cd()

        for i,ii in enumerate(ipreds) :
            self.main_hist.plots[ii].SetDrawOption('lE3')           
            self.main_hist.plots[ii].Draw('lE3')                    
            self.main_hist.plots[ii].SetMarkerSize(1)               
            self.main_hist.plots[ii].SetMarkerColor(color[icol[i]])       
            self.main_hist.plots[ii].SetLineColor  (color[icol[i]])       
            self.main_hist.plots[ii].SetFillColor  (color[icol[i]])       
            self.main_hist.plots[ii].SetLineWidth(2)                
            self.main_hist.plots[ii].SetFillStyle(3001)             
            self.main_hist.plots[ii].SetMarkerStyle(markerstyles[icol[i]])
        for i,ii in enumerate(iregs) :
            self.main_hist.plots[ii].SetDrawOption('p')             
            self.main_hist.plots[ii].Draw('p')                      
            self.main_hist.plots[ii].SetMarkerSize(1)               
            self.main_hist.plots[ii].SetMarkerColor(color[icol[i]])       
            self.main_hist.plots[ii].SetLineColor  (color[icol[i]])       
            self.main_hist.plots[ii].SetMarkerStyle(markerstyles[icol[i]])
        for i,ii in enumerate(ifoods) :
            self.main_hist.plots[ii].SetDrawOption('histsames')     
            self.main_hist.plots[ii].Draw('histsames')              
            self.main_hist.plots[ii].SetMarkerColor(color[icol[i]])       
            self.main_hist.plots[ii].SetLineColor  (color[icol[i]])       
            self.main_hist.plots[ii].SetMarkerStyle(markerstyles[icol[i]])

        return

    def GetDay(self,days) :
        self.TurnOffDays()
        self.SetGraphs(days)
        self.main_hist.can.Draw()

    def Mon(self) :
        self.GetDay(['Monday'])
    def Tues(self) :
        self.GetDay(['Monday','Tuesday'])
    def Wed(self) :
        self.GetDay(['Tuesday','Wednesday'])
    def Thurs(self) :
        self.GetDay(['Wednesday','Thursday'])
    def Fri(self) :
        self.GetDay(['Thursday','Friday'])
    def Sat(self) :
        self.GetDay(['Friday','Saturday'])
    def Sun(self) :
        self.GetDay(['Saturday','Sunday'])
    def all(self) :
        self.SetGraphs()

    def m(self) :
        return self.Mon()
    def t(self) :
        return self.Tues()
    def w(self) :
        return self.Wed()
    def th(self) :
        return self.Thurs()
    def f(self) :
        return self.Fri()
    def s(self) :
        return self.Sat()
    def su(self) :
        return self.Sun()

    def Overview(self,d1) :
        if d1 == 'last' :
            print 'last week was',last_week
            return self.GetOverview(last_week,last_week)
        return self.GetOverview(d1,d1)

    def GetOverview(self,d1,d2) :

        graphs = []
        hists_fine = []
        hists_coarse = []
        req = 'BGReading > 0 && %d <= WeekOfYear && WeekOfYear <= %d'%(d1,d2)
        n = e.Draw('BGReading:TimeOfDayFromFourAM>>hist%d%d(50,-0.5,24.5,41,40,450)'%(d1,d2),req,'goff')
        if not n : return None
        graphs.append(TGraph(n,e.GetV2(),e.GetV1()))

        Avg = 0
        for x in range(n) :
            Avg += e.GetV1()[x]
        Avg = Avg / float(n)

        hists_fine.append(gDirectory.Get('hist%d%d'%(d1,d2)))
        key = 'coarse hist %d %d'%(d1,d2)
        hists_coarse.append(TH2F(key,key,ltime,array('d',time_bins),lbg,array('d',bg_bins)))
        hists_coarse[-1].GetZaxis().SetLabelFont(42)
        smallest_bin = 0
        for j in range(hists_fine[-1].GetNbinsX()) :
            c_x = list(hists_fine[-1].GetXaxis().GetBinLowEdge(j+1) < a for a in time_bins).index(True)
            for k in range(hists_fine[-1].GetNbinsY()) :
                c_y = list(hists_fine[-1].GetYaxis().GetBinLowEdge(k+1) < a for a in bg_bins).index(True)
                val = hists_fine[-1].GetBinContent(j+1,k+1)
                if val : 
                    hists_coarse[-1].SetBinContent(c_x,c_y,val+hists_coarse[-1].GetBinContent(c_x,c_y))

        nametitle = 'Week %d (N=%d)'%(d1,graphs[-1].GetN())
        graphs[-1].SetNameTitle(nametitle,nametitle)

        title = '%s (N=%d, \mu=%0.1f).'%(t.GetWeeksString(d1,d2),graphs[-1].GetN(),Avg)

        if 'plain_hist' in dir(self) :
            self.old_plain_hists.append(self.plain_hist)

        self.plain_hist = SmartPlot(0,'',title,[hist,hists_coarse[-1],graphs[-1]],ranges=[[0,24],[0,450]],drawopt='colz')
        self.plain_hist.plots[2].SetDrawOption('p')
        self.plain_hist.plots[2].SetMarkerColor(1)
        self.plain_hist.DrawHorizontal(80.)
        self.plain_hist.DrawHorizontal(160.)

        return

    def Detailed(self,d1) :
        if d1 == 'last' :
            print 'last week was',last_week
            return self.GetDetailed(last_week,last_week)
        return self.GetDetailed(d1,d1)

    def VeryDetailed(self,week,d1) : # i.e. 19,0
        pass

    def GetDailyTotals(self) :
        # DailyInsulinTotal
        pass

    def DoSample(self) :

        tf1s = []
        ntest = 3
        for x in range(ntest) :
            #
            # Overrides
            #
            self.start_of_plot_day = t.WeekDayHourToUniversal(0,x,0)
            self.containers = []

            NFOOD = [45,130,60,100]
            RATIO = 16

            # test for early bolus
            #FACTOR = [1,1,1]
            #OFFSET = [0,0.25,0.5]
            #NAMES = ['Nominal','15min Early Bolus','30min Early Bolus']

            # test for reducing food
            FACTOR = [1,0.5,0.5]
            OFFSET = [0,0,0.5]
            #NAMES = ['Nominal','3/4 Carb Intake','1/2 Carb Intake']
            NAMES = ['Nominal','1/2 Carb Intake','1/2 Carb + E.B.']

            #
            # starting bg OF DAY
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,0)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,1)
            self.containers[-1].type     = 'First BG'
            self.containers[-1].const_BG = 115.
            
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,1)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,23)
            self.containers[-1].type     = 'BGReading'
            self.containers[-1].const_BG = 115.

            #
            # breakfast
            #
            meal = 0
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,5-OFFSET[x]) # 9am
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,11)
            self.containers[-1].type     = 'Insulin'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 4.
            self.containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,5) # 9am
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,11)
            self.containers[-1].type     = 'Food'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 2.
            self.containers[-1].C        = NFOOD[meal]*FACTOR[x]
            self.containers[-1].RIC      = RATIO

            #
            # lunch
            #
            meal = 1
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,8-OFFSET[x])
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,14)
            self.containers[-1].type     = 'Insulin'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 4.
            self.containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,8)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,14)
            self.containers[-1].type     = 'Food'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 2.
            self.containers[-1].C        = NFOOD[meal]*FACTOR[x]
            self.containers[-1].RIC      = RATIO

            #
            # snack
            #
            meal = 2
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,12-OFFSET[x])
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,18)
            self.containers[-1].type     = 'Insulin'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 4.
            self.containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,12)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,18)
            self.containers[-1].type     = 'Food'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 2.
            self.containers[-1].C        = NFOOD[meal]*FACTOR[x]
            self.containers[-1].RIC      = RATIO

            #
            # dinner
            #
            meal = 3
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,16-OFFSET[x])
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,22)
            self.containers[-1].type     = 'Insulin'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 4.
            self.containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,16)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,22)
            self.containers[-1].type     = 'Food'
            self.containers[-1].S        = 65.
            self.containers[-1].Ta       = 2.
            self.containers[-1].C        = NFOOD[meal]*FACTOR[x]
            self.containers[-1].RIC      = RATIO

            #
            # "final reading"
            #
            self.containers.append(BGFunction())
            self.containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,23)
            self.containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,25)
            self.containers[-1].type     = 'BGReading'
            self.containers[-1].const_BG = 115.

            print x
            tf1s.append(self.GetPredictionPlots(0,x))
            key = NAMES[x]+' (IBG=%2.2f)'%GetIntegratedAverage(tf1s[-1])
            tf1s[-1].SetNameTitle(key,key)
            #daytitle = daytitles.get(x,'Noneday')
            #key = daytitle+' sample'
            #tf1s[-1].SetNameTitle(key,key)

        tf1sNOASYM = []
        for i in range(len(tf1s)) :
            tf1sNOASYM.append(TGraph(tf1s[i].GetN(),tf1s[i].GetX(),tf1s[i].GetY()))
            key = tf1s[i].GetName()
            tf1sNOASYM[-1].SetNameTitle(key,key)

        self.sample_hist = SmartPlot(0,'','Reduced Carbohydrate Example',[hist]+tf1sNOASYM,ranges=[[0,24],[40,450]],drawopt='')
        for i in range(ntest) :
            self.sample_hist.plots[i+1].SetDrawOption('p')
            self.sample_hist.plots[i+1].SetMarkerColor(color[i])
            self.sample_hist.plots[i+1].SetLineColor(color[i])
        self.sample_hist.createLegend(.5,.65,.95,.88)
        self.sample_hist.SetLegend(skip=[0])
        self.sample_hist.can.cd()
        self.sample_hist.leg.Draw()
        self.sample_hist.SetAxisLabels('Time','BG')

    def CHECK(self) :
        print self.dump[0].GetX()[1]

    def GetDetailed(self,d1,d2) :
        graphs = []
        hists_fine = []
        hists_coarse = []
        Avg = 0
        N = 0
        key = 'coarse hist %d %d'%(d1,d2)
        hists_coarse.append(TH2F(key,key,ltime,array('d',time_bins),lbg,array('d',bg_bins)))
        hists_coarse[-1].GetZaxis().SetLabelFont(42)

        tf1s = []
        tf1food = []

        #print 'month',d1

        for x in range(7) :

            #print 'day',x

            req = 'BGReading > 0 && %d <= WeekOfYear && WeekOfYear <= %d && DayOfWeekFromMonday == %d'%(d1,d2,x)
            n = e.Draw('BGReading:TimeOfDayFromFourAM>>hist%d%d%d(50,-0.5,24.5,41,40,450)'%(d1,d2,x),req,'goff')
            if not n : continue
            graphs.append(TGraph(n,e.GetV2(),e.GetV1()))

            for xx in range(n) :
                Avg += e.GetV1()[xx]

            N += n

            hists_fine.append(gDirectory.Get('hist%d%d%d'%(d1,d2,x)))

            smallest_bin = 0
            for j in range(hists_fine[-1].GetNbinsX()) :
                c_x = list(hists_fine[-1].GetXaxis().GetBinLowEdge(j+1) < a for a in time_bins).index(True)
                for k in range(hists_fine[-1].GetNbinsY()) :
                    c_y = list(hists_fine[-1].GetYaxis().GetBinLowEdge(k+1) < a for a in bg_bins).index(True)
                    val = hists_fine[-1].GetBinContent(j+1,k+1)
                    if val : 
                        hists_coarse[-1].SetBinContent(c_x,c_y,val+hists_coarse[-1].GetBinContent(c_x,c_y))

            daytitle = daytitles.get(x,'Noneday')

            graphs[-1].SetNameTitle(daytitle,daytitle)
            #graphs[-1].SetMarkerStyle(20)

            self.LoadDayEstimateDDX(d1,x)
            tf1s.append(self.GetPredictionPlots(d1,x))
            tf1food.append(self.GetFoodPlots(d1,x))
            key = daytitle+' prediction'
            tf1s[-1].SetNameTitle(key,key)
            key = daytitle+' food'
            tf1food[-1].SetNameTitle(key,key)

        if N == 0 : return

        Avg = Avg / float(N)
        nametitle = 'Week %d (N=%d)'%(d1,N)
        title = '%s (N=%d, \mu=%0.1f)'%(t.GetWeeksString(d1,d2),N,Avg)

        if 'main_hist' in dir(self) :
            self.old_main_hists.append(self.main_hist)

        self.main_hist = SmartPlot(0,'',title,[hist,hists_coarse[-1]]+graphs,ranges=[[0,24],[0,450]],drawopt='colz')

        self.main_hist.can.SetCanvasSize(1000,700)
        self.main_hist.DrawHorizontal(80.)
        self.main_hist.createLegend(.6,.65,.85,.88)
        self.main_hist.SetLegend(skip=[0,1])
        self.main_hist.can.cd()
        self.main_hist.leg.Draw()
        self.main_hist.DrawHorizontal(160.)
        self.main_hist.DrawHorizontal(115.,style=3)
        self.main_hist.plots[0].GetYaxis().SetRangeUser(0,450)

        #
        # Add prediciton graphs
        #
        self.main_hist.ngraphs = len(graphs)
        for i in range(len(graphs)) :
            self.main_hist.plots.append(tf1s[i])
            self.main_hist.can.cd()
            self.main_hist.plots[-1].Draw('lE3') # draw option later in SetGraphs
            self.main_hist.plots[2+i].Draw("p") # draw option later in SetGraphs

        #
        # Add food graphs
        #
        for i in range(len(graphs)) :
            self.main_hist.plots.append(tf1food[i])
            self.main_hist.can.cd()
            self.main_hist.plots[-1].Draw('histsames')

        self.SetGraphs()
        return

    #
    # Fill all the containers for information before doing the predictive part
    #
    def LoadDayEstimateDDX(self,week,day) :
        #
        # Look for any event between midnight of the previous day and 4am of the next day.
        #
        #self.start_time = t.WeekDayHourToUniversal(week,day,0)  # idk
        #print 'self.start_time DDX', self.start_time
        #start_time_rr = self.start_time                          # relevant readings - will change

        self.start_of_plot_day = t.WeekDayHourToUniversal(week,day,0) # from 4am
        end_time = t.WeekDayHourToUniversal(week,day+1,0)   # events ending at 4am

        self.containers = []

        #
        # BG Readings - get carry-over.
        #
        for i in range(e.GetEntries()) :
            e.GetEntry(i)
            if e.UniversalTime < self.start_of_plot_day : continue
            if e.UniversalTime > end_time : continue
            if e.BGReading > 0 :
                #
                # the iov_1 is the iov_0 of this first measurement
                #
                UT_next = e.UniversalTime
                for j in range(i-1,0,-1) :
                    e.GetEntry(j)
                    if e.BGReading > 0 :
                        bg_read = e.BGReading
                        break

                self.containers.append(BGFunction())
                self.containers[-1].iov_0 = e.UniversalTime
                self.containers[-1].type = 'First BG'
                start_time_rr = e.UniversalTime - 6.*t.OneHour # start collecting 6h before first meas.
                self.containers[-1].const_BG = bg_read
                self.containers[-1].iov_1 = UT_next


                break
            #
        #

        #
        # Get the rest of the points
        #
        for i in range(e.GetEntries()) :
            e.GetEntry(i)
            #print 'time',t.StringFromTime(e.UniversalTime),'BG',e.BGReading
            if e.UniversalTime < start_time_rr : continue
            #
            # Should not need this
            #
            #if e.UniversalTime < self.start_of_plot_day and e.BGReading > 0 : continue # skip earlier meas.
            if e.UniversalTime > end_time : continue

            if e.BGReading > 0 and e.UniversalTime > self.start_of_plot_day :
                self.containers.append(BGFunction())
                self.containers[-1].type = 'BGReading'
                self.containers[-1].const_BG = e.BGReading
                self.containers[-1].iov_0 = e.UniversalTime

                #
                # find next meas
                #
                UT_next = t.StartOfYear + t.OneYear # end of the year
                for j in range(i+1,e.GetEntries()) :
                    e.GetEntry(j)
                    if e.BGReading > 0 :
                        UT_next = e.UniversalTime
                        break
                self.containers[-1].iov_1 = UT_next

            #
            # Insulin mothafucka
            #
            if e.BWZEstimate > 0 :

                self.containers.append(BGFunction())
                self.containers[-1].type  = 'Insulin'
                self.containers[-1].iov_0 = e.UniversalTime
                self.containers[-1].iov_1 = e.UniversalTime+6.*t.OneHour
                self.containers[-1].S     = e.BWZInsulinSensitivity
                self.containers[-1].Ta    = 4.
                self.containers[-1].I0    = e.BWZEstimate

            #
            # Food bitch!
            #
            if e.BWZCarbInput > 0 :

                self.containers.append(BGFunction())
                self.containers[-1].type  = 'Food'
                self.containers[-1].iov_0 = e.UniversalTime
                self.containers[-1].iov_1 = e.UniversalTime+6.*t.OneHour
                self.containers[-1].S     = e.BWZInsulinSensitivity
                self.containers[-1].Ta    = 2.
                self.containers[-1].C     = e.BWZCarbInput
                self.containers[-1].RIC   = e.BWZCarbRatio

        #
        # Now make the prediction plots (moved elsewhere)
        #
        return

    #
    # Returns a histo with the food in a day
    #
    def GetFoodPlots(self,week,day) :
        #
        # start and end of day in universal
        #
        self.start_of_plot_day = t.WeekDayHourToUniversal(week,day,0) # from 4am
        end_time = t.WeekDayHourToUniversal(week,day+1,0)   # events ending at 4am

        key = 'food %s %s'%(week,day)
        food = TH1F(key,key,250,-0.5,24.5)
        for c in self.containers :
            if c.C :
                if c.iov_0 > self.start_of_plot_day and c.iov_0 < end_time :
                    food.AddBinContent(food.FindBin(t.GetTimeOfDay(c.iov_0)),c.C)
        return food

    #
    # The standard prediction plots for week
    # Returns one plot, for one day, with the predicted levels
    #
    def GetPredictionPlots(self,week,day) :

        hours_per_step = .1
        x_time = []
        y_bg = []
        y_bg_err_up = []
        y_bg_err_dn = []
        
        # print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        # print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        # print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

#         for c in self.containers :
#             c.Print()

        for i in range(int(24./hours_per_step)) :
            # print 'self.start_of_plot_day',self.start_of_plot_day
            the_time = self.start_of_plot_day + i*hours_per_step*float(t.OneHour) # universal

            # print 'the_time',t.StringFromTime(the_time)

            x_time.append(0+hours_per_step*i)
            if len(y_bg) : 
                y_bg.append(y_bg[-1])
                y_bg_err_up.append(y_bg_err_up[-1])
                y_bg_err_dn.append(y_bg_err_dn[-1])
            else : 
                y_bg.append(0)
                y_bg_err_up.append(0)
                y_bg_err_dn.append(0)

#             print '%%%%%%%%%%%%%%%%%%%%%%%%%%%'
#             print the_time,t.StringFromTime(the_time),'xtime:',x_time[-1]
#             print '%%%%%%%%%%%%%%%%%%%%%%%%%%%'

            #
            # Find the last measurement time
            #
            last_meas_time = the_time
            for c in self.containers :
                if c.type == 'First BG' :
                    last_meas_time = c.iov_0
                    break

            for c in self.containers :

                #c.Print()

                if the_time < c.iov_0 : continue

                if (i==0) and (c.I0 or c.C) :
                    nom_integral = c.getIntegral(the_time            ) - c.getIntegral(last_meas_time            )
                    # up_integral  = c.getIntegral(the_time,RIC_fac=self.RIC_fac_up) - c.getIntegral(last_meas_time,RIC_fac=self.RIC_fac_up)
                    # dn_integral  = c.getIntegral(the_time,RIC_fac=self.RIC_fac_dn) - c.getIntegral(last_meas_time,RIC_fac=self.RIC_fac_dn)
                    up_integral  = c.getIntegral(the_time,RIC_n=self.RIC_n_up) - c.getIntegral(last_meas_time,RIC_n=self.RIC_n_up)
                    dn_integral  = c.getIntegral(the_time,RIC_n=self.RIC_n_dn) - c.getIntegral(last_meas_time,RIC_n=self.RIC_n_dn)
                    y_bg[-1] += nom_integral
                    y_bg_err_up[-1] += up_integral - nom_integral
                    y_bg_err_dn[-1] += nom_integral - dn_integral
                    continue

                if the_time > c.iov_1 : continue

                if c.I0 or c.C :
                    nom_ddx = c.getDDXtimesInterval(the_time,hours_per_step)
                    up_ddx = c.getDDXtimesInterval(the_time,hours_per_step,RIC_n=self.RIC_n_up)
                    dn_ddx = c.getDDXtimesInterval(the_time,hours_per_step,RIC_n=self.RIC_n_dn)
                    y_bg[-1] += nom_ddx
                    y_bg_err_up[-1] += up_ddx - nom_ddx
                    y_bg_err_dn[-1] += nom_ddx - dn_ddx
                if c.const_BG and not c.Registered : 
                    y_bg[-1] = c.const_BG
                    y_bg_err_up[-1] = 0.
                    y_bg_err_dn[-1] = 0.
                    c.Registered = True

        x_bg_err_up = []
        x_bg_err_dn = []
        for i in range(len(x_time)) :
            x_bg_err_up.append(0)
            x_bg_err_dn.append(0)

        x_time_d = array('d',x_time)
        y_bg_d   = array('d',y_bg  )
        y_bg_d_err_up = array('d',y_bg_err_up)
        y_bg_d_err_dn = array('d',y_bg_err_dn)

        x_bg_d_err_up = array('d',x_bg_err_up)
        x_bg_d_err_dn = array('d',x_bg_err_dn)

        myddx = TGraphAsymmErrors(len(x_time)-1,x_time_d,y_bg_d,
                                  x_bg_d_err_up,x_bg_d_err_dn,y_bg_d_err_up,y_bg_d_err_dn)

        return myddx




class BGFunction :
    def __init__(self) :
        self.type = 'Unknown'
        self.iov_0 = 0 # universal time
        self.iov_1 = 0 # universal time
        self.const_BG = 0
        self.S = 0 # sensitivity
        self.Ta = 4. # active insulin time
        self.I0 = 0.
        self.C = 0.
        self.RIC = 0.
        self.Registered = None
        return

    def getEffectiveSensitivity(self,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        if self.I0 :
            return - self.I0 * self.S * S_fac
        #
        # Food
        #
        return C_fac * S_fac * self.C * self.S / float( (self.RIC + RIC_n) * RIC_fac)

    #
    # Function to help with the first bit of the histogram
    #
    def getIntegral(self,time,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        if time < self.iov_0 : return 0.
        #if time > self.iov_1 : return 0.
        
        time_hr = (time-self.iov_0)/float(t.OneHour)
        
        result = 1
        result -= math.pow(0.05,math.pow(time_hr/self.Ta,2))
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
        #print 'returning result',result
        return result

    def getDDXtimesInterval(self,time,delta,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        #time += delta
        if time < self.iov_0 : return 0.
        if time > self.iov_1 : return 0.

        time_hr = (time-self.iov_0)/float(t.OneHour)
        
        result = 2*math.pow((1/self.Ta),2)
        result *= 3.0 # ln 20
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
        result *= time_hr
        result *= math.pow(0.05,math.pow(time_hr/self.Ta,2))
        #result *= (time_hr < 6)
        result *= delta
        #print 'returning result',result
        return result

    def Print(self) :

        print '-------------'
        print 'type ',self.type 
        print 'iov_0',self.iov_0,t.StringFromTime(self.iov_0)
        print 'iov_1',self.iov_1,t.StringFromTime(self.iov_1)
        print 'BG   ',self.const_BG
        print 'S    ',self.S    
        print 'Ta   ',self.Ta   
        print 'I0   ',self.I0
        print 'Reg  ',self.Registered

        return
                
c = WeekPlot()
