import time
from array import array
import ROOT
from Settings import SettingsHistograms

class UNIXcolor:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    def bold(text) :
        return UNIXcolor.BOLD + text + UNIXcolor.END

#------------------------------------------------------------------
class TimeClass :
    def __init__(self) :
        self.StartOfYear = self.TimeFromString("12/31/12 04:00:00")
        self.OneSecond   = self.TimeFromString("12/31/12 04:00:01") - self.StartOfYear
        self.OneMinute   = self.TimeFromString("12/31/12 04:01:00") - self.StartOfYear
        self.OneHour     = self.TimeFromString("12/31/12 05:00:00") - self.StartOfYear
        self.OneDay      = self.TimeFromString("01/01/13 04:00:00") - self.StartOfYear
        self.OneWeek     = self.TimeFromString("01/07/13 04:00:00") - self.StartOfYear
        self.OneYear     = self.TimeFromString("12/31/13 04:00:00") - self.StartOfYear
        self.timerightnow = long(time.mktime(time.localtime()))
        self.MillisecondsInAnHour = 60*60*1000 # 3600000
        
        return

    def WeeksOld(self,universaltime) :
        return (self.timerightnow - universaltime) / self.OneWeek

    def GetWeekOfYear(self,l) :
        # starting from week 0
        l = long(l)
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return (l - self.StartOfYear + is_dst*self.OneHour) / self.OneWeek

    def nWeekToUniversal(self,week) :
        l = self.OneWeek*week + self.StartOfYear
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return l - is_dst*self.OneHour

    def DayWeekToUniversal(self,week,day) :
        return self.nWeekToUniversal(week) + self.OneDay*day

    def GetDayOfWeek(self,l) :
        l = long(l)
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return (l + is_dst*self.OneHour - self.GetWeekOfYear(l)*self.OneWeek - self.StartOfYear) / self.OneDay

    def GetHourOfDay(self,l) :
        l = long(l)
        return time.localtime(l-self.OneHour*4).tm_hour

    def GetTimeOfDay(self,l) :
        # Starting from 4am
        l = long(l)-self.OneHour*4.
        return time.localtime(l).tm_hour + time.localtime(l).tm_min/60.

    def GetTimeOfDayFromMidnight(self,l) :
        # Starting from 4am
        return time.localtime(l).tm_hour + time.localtime(l).tm_min/60.

    def TimeFromString(self,s) :
        # universal
        try :
            return long(time.mktime(time.strptime(s, "%m/%d/%y %H:%M:%S")))
        except ValueError :
            try :
                # Tidepool format
                return long(time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%S')))
            except ValueError :
                print 'Error: could not convert to UTC: %s'%(s)
                import sys; sys.exit()
    
    def StringFromTime(self,t,dayonly=False) :
        if dayonly :
            return time.strftime("%m/%d/%y",time.localtime(t))
        return time.strftime("%m/%d/%y %H:%M:%S",time.localtime(t))

    def GetWeekString(self,w) :
        start = time.localtime(self.StartOfYear+self.OneWeek*w)
        end = time.localtime(self.StartOfYear+self.OneWeek*(w+1)-self.OneHour*12)
        return '%s to %s'%(time.strftime('%a, %b %d',start),time.strftime('%a, %b %d',end))

    def GetWeeksString(self,w1,w2) :
        start = time.localtime(self.StartOfYear+self.OneWeek*w1)
        end = time.localtime(self.StartOfYear+self.OneWeek*(w2+1)-self.OneHour*12)
        return '%s to %s'%(time.strftime('%a, %b %d',start),time.strftime('%a, %b %d',end))

    def WeekDayHourToUniversal(self,week,day,hour,minute=0) :
        # Hour after 4am
        return self.nWeekToUniversal(week) + day*self.OneDay + hour*self.OneHour + minute*self.OneMinute

# Do not worry - if you import this file multiple times, you will not create multiple instances.
# The module will be loaded once, and each subsequent "import" will just link the file to
# the static state of the first-imported file.
MyTime = TimeClass()

#------------------------------------------------------------------
def a1cToBS(n,formula_type='Kurt') :
    if formula_type == 'ADA' :
        return 28.71*(n-7)+154.42,'28.71*(n-7)+154.42'
    elif formula_type == 'Kurt' :
        return 45.00*(n-7)+149.00,'45.00*(n-7)+149.00'
    return 35.6*(n-7)+171.90,'35.6*(n-7)+171.90'

#------------------------------------------------------------------
def RootMeanSquare(vals) :
    import math
    avg = sum(vals)/float(len(vals))
    return math.sqrt(sum(list(math.pow(a-avg,2) for a in vals))/float(len(vals)))

#------------------------------------------------------------------

def GetHistWithTimeAxis() :
    import ROOT
    if ROOT.gDirectory.Get('HistWithTimeAxis') :
        return ROOT.gDirectory.Get('HistWithTimeAxis')
    hist= ROOT.TH1F('HistWithTimeAxis','remove',25,-0.5,24.5)
    hist.GetXaxis().SetBinLabel(1,'4 am                   ')
    hist.GetXaxis().SetBinLabel(5,'8 am')
    hist.GetXaxis().SetBinLabel(9,'12 pm')
    hist.GetXaxis().SetBinLabel(13,'4 pm')
    hist.GetXaxis().SetBinLabel(17,'8 pm')
    hist.GetXaxis().SetBinLabel(21,'12 am')
    return hist

#------------------------------------------------------------------
def GetIntegratedAverage(graph) :
    #
    # Get the "integrated" average from a TGraph with constant steps.
    #
    tot = 0
    n = 0
    for i in range(graph.GetN()) :
        if graph.GetY()[i] :
            tot += graph.GetY()[i]
            n += 1
    return tot/float(n)

#------------------------------------------------------------------
class BGFunction :
    #
    # 
    #
    def __init__(self,_type,iov_0=0,iov_1=0,const_BG=0,Ta=4.,I0Est=0.,S=60.) :
        self.type = _type  # The type ('First BG','BGReading','Insulin','Food')
        self.iov_0 = iov_0 # universal time - start of interval of validity
        self.iov_1 = iov_1 # universal time - end of interval of validity
        self.const_BG = const_BG # real BG reading
        self.S = S      # sensitivity
        self.Ta = Ta    # active insulin time
        self.I0Est = I0Est # Bolus wizard estimate
        self.I0 = 0.    # Bolus volume delivered
        self.C = 0.     # carb input (grams)
        self.RIC = 0.
        #
        self.BWZCorrectionEstimate = 0.
        self.BWZFoodEstimate = 0.
        self.BWZActiveInsulin = 0.
        self.BWZBGInput = 0.
        self.BWZMatchedDelivered = True
        return

    def getEffectiveSensitivity(self,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        #
        #
        #
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
        #
        # Return the integral of the BG function
        # RIC_fac: increase the insulin-carb ratio (
        #
        import math
        if time < self.iov_0 : return 0.
        #if time > self.iov_1 : return 0.
        
        time_hr = (time-self.iov_0)/float(MyTime.OneHour)
        
        result = 1
        result -= math.pow(0.05,math.pow(time_hr/float(self.Ta),2))
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
        #print 'returning result',result
        return result

    def bgImpactRemaining(self,time,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        
        return (self.getIntegral(time,S_fac,C_fac,RIC_fac,RIC_n) -
                self.getIntegral(time*1000,S_fac,C_fac,RIC_fac,RIC_n)) # "infinity"

    def getBGImpactDerivPerHour(self,time_ut) :
        import math

        if (time_ut < self.iov_0) or (time_ut > self.iov_1) :
            return 0.

        time_hr = (time_ut-self.iov_0)/float(MyTime.OneHour)
        
        result = 2*math.pow((1/float(self.Ta)),2)
        result *= 3.0 # ln 20
        result *= self.getEffectiveSensitivity()
        result *= time_hr
        result *= math.pow(0.05,math.pow(time_hr/float(self.Ta),2))

        return result

    def getBGImpactDerivTimesInterval(self,time_ut,delta_hr) :

        return self.getBGImpactDerivPerHour(time_ut) * delta_hr

    def Print(self) :

        print '-------------'
        print 'type ',self.type 
        print 'iov_0',self.iov_0,MyTime.StringFromTime(self.iov_0)
        print 'iov_1',self.iov_1,MyTime.StringFromTime(self.iov_1)
        print 'BG   ',self.const_BG
        print 'S    ',self.S    
        print 'Ta   ',self.Ta   
        print 'I0   ',self.I0
        print 'C    ',self.C
        if self.I0 or self.C :
            print 'Effective BG',self.getEffectiveSensitivity()
            print 'BG Integral',self.getIntegral(self.iov_1)
            hours_per_step = 0.2
            ddxes = []
            for i in range(int(6./hours_per_step)) :
                ddxes.append(self.getBGImpactDerivTimesInterval(self.iov_0+i*hours_per_step*float(MyTime.OneHour),hours_per_step))
            print 'BG ddX * delta',sum ( ddxes )

        return

    def PrintBolus(self) :

        star = ' *' if not self.BWZMatchedDelivered else ''
        decaytime = ' %d hour decay'%(self.Ta) if (self.Ta > 4) else ''
        print 'Bolus, %s (input BG: %d mg/dl) (S=%d)'%(MyTime.StringFromTime(self.iov_0),self.BWZBGInput,self.S)

        def PrintDetails(title,item,postscript='') :
            print title + ('%2.1f u;'%(item)).rjust(10)+(' %2.1f mg/dl'%(item*self.S)).rjust(15)+(' %2.1f g'%(item*self.RIC)).rjust(10)+postscript
            return

        PrintDetails('  Total Delivered insulin : ',self.I0,star)
        PrintDetails('  Total Suggested insulin : ',self.I0Est)
        PrintDetails('             food insulin : ',self.BWZFoodEstimate,decaytime)
        PrintDetails('       correction insulin : ',self.BWZCorrectionEstimate)
        PrintDetails('           active insulin : ',self.BWZActiveInsulin)
        print

        return


#------------------------------------------------------------------
def GetDataFromDay(tree,data_type,day_of_week,week_of_years) :
    import ROOT
    from array import array
    req = '%s > 0 && %d <= WeekOfYear && WeekOfYear <= %d && DayOfWeekFromMonday == %d'%(data_type,week_of_years,week_of_years,day_of_week)
    n = tree.Draw('%s:TimeOfDayFromFourAM>>hist%d%d%d(50,-0.5,24.5,41,40,450)'%(data_type,week_of_years,week_of_years,day_of_week),req,'goff')
    if not n :
        return ROOT.TGraph(1,array('d',[1]),array('d',[1]))
    data = ROOT.TGraph(n,tree.GetV2(),tree.GetV1())
    day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    data.SetName('%s_%s_%d'%(data_type,day[day_of_week],week_of_years))
    return data

#------------------------------------------------------------------
def ColorHistsAccordingToDay(canvas) :
    import ROOT
    colors = {'Monday'   :ROOT.kBlack+0,
              'Tuesday'  :ROOT.kRed+1,
              'Wednesday':ROOT.kAzure-2,
              'Thursday' :ROOT.kGreen+1,
              'Friday'   :ROOT.kMagenta+1,
              'Saturday' :ROOT.kCyan+1,
              'Sunday'   :ROOT.kOrange+1,
              }
    for i in canvas.GetListOfPrimitives() :
        found_col = ''
        for c in colors.keys() :
            if c in i.GetName() :
                found_col = c
        if not found_col :
            continue
        if hasattr(i,'SetLineColor') :
            i.SetLineColor(colors[found_col])
        if hasattr(i,'SetMarkerColor') :
            i.SetMarkerColor(colors[found_col])
        if hasattr(i,'SetFillColor') :
            i.SetFillColor(colors[found_col])
    return

#------------------------------------------------------------------
def GetLastWeek(tree) :
    last_week = 0
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        last_week = max(last_week,tree.WeekOfYear)
    return last_week

#------------------------------------------------------------------
def ThreePadCanvas(canvas_name,canvas_title,canw=500,canh=600,ratio_1=0.28,ratio_2=0.5,ratio_n1=0) :
    from ROOT import TCanvas,TPad
    from PlotFunctions import tobject_collector

    c = TCanvas(canvas_name,canvas_title,canw,canh)
    c.cd()
    top = TPad("pad_top", "This is the top pad",0.0,ratio_2,1.0,1.0)
    top.SetBottomMargin(0.005/float(top.GetHNDC()))
    top.SetTopMargin   (0.04/float(top.GetHNDC()))
    top.SetRightMargin (0.05 )
    top.SetLeftMargin  (0.16 )
    top.SetFillColor(0)
    top.Draw()
    tobject_collector.append(top)

    c.cd()
    bot = TPad("pad_mid", "This is the middle pad",0.0,ratio_1,1.0,ratio_2)
    bot.SetBottomMargin(0.005/float(bot.GetHNDC()))
    bot.SetTopMargin   (0.005/float(bot.GetHNDC()))
    bot.SetRightMargin (0.05)
    bot.SetLeftMargin  (0.16)
    bot.SetFillColor(0)
    bot.Draw()
    tobject_collector.append(bot)
    
    c.cd()
    bot = TPad("pad_bot", "This is the bottom pad",0.0,ratio_n1,1.0,ratio_1)
    bot.SetBottomMargin(0.08/float(bot.GetHNDC()))
    bot.SetTopMargin   (0.005/float(bot.GetHNDC()))
    bot.SetRightMargin (0.05)
    bot.SetLeftMargin  (0.16)
    bot.SetFillColor(0)
    bot.Draw()
    tobject_collector.append(bot)

    if ratio_n1 :
        c.cd()
        sub = TPad("pad_sub", "This is the sub-bottom pad",0.0,0.0,1.0,ratio_n1)
        sub.SetBottomMargin(0.03)
        sub.SetTopMargin   (0.01)
        sub.SetRightMargin (0.05)
        sub.SetLeftMargin  (0.16)
        sub.SetFillColor(0)
        sub.Draw()
        tobject_collector.append(sub)

    return c

#------------------------------------------------------------------
def GetMidPad(can) :
    return can.GetPrimitive('pad_mid')

#------------------------------------------------------------------
def PredictionCanvas(tree,day,weeks_ago=0,rootfile=0) :
    print 'Calculating the prediction from day-of-week %d of %d weeks ago'%(day,weeks_ago)
    import PlotFunctions as plotfunc
    import TAxisFunctions as taxisfunc
    from array import array

    prediction_canvas = ThreePadCanvas('prediction_canvas','prediction_canvas',600,600,
                                       ratio_1=0.41,
                                       ratio_2=0.59,
                                       ratio_n1=0.17
                                       )

    week = GetLastWeek(tree)
    week = week - weeks_ago
    
    # Add Time axis histogram to each sub-pad
    plotfunc.AddHistogram(prediction_canvas,GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(plotfunc.GetBotPad(prediction_canvas),GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),GetHistWithTimeAxis(),'')

    # Quick function to make target zones
    def MakeErrorBandHistogram(name,min,max,color) :
        average = (min + max) / float(2)
        difference = (min - max)
        band = ROOT.TH1F(name,'skipme',1,-0.5,24.5)
        band.SetBinContent(1,average)
        band.SetBinError(1,difference/float(2))
        band.SetFillColor(color)
        band.SetMarkerSize(0)
        return band

    # Green and yellow target zones
    bandYellow = MakeErrorBandHistogram('yellow',80,180,ROOT.kOrange)
    bandGreen  = MakeErrorBandHistogram('yellow',100,150,ROOT.kGreen)
    plotfunc.AddHistogram(prediction_canvas,bandYellow,'E2')
    plotfunc.AddHistogram(prediction_canvas,bandGreen,'E2')
    plotfunc.GetTopPad(prediction_canvas).RedrawAxis()

    # Sensor data (if available)
    sensor_data = GetDataFromDay(tree,'SensorGlucose',day,week)
    sensor_data.SetMarkerSize(0.7)
    if sensor_data.GetN() > 1 :
        plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),sensor_data,'p')

    # BG data
    bg_data = GetDataFromDay(tree,'BGReading',day,week)
    bg_data.SetMarkerColor(ROOT.kRed+1)
    plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),bg_data,'p')

    containers = GetDayContainers(tree,week,day)

    # Make the prediction plot (including error bars)
    prediction_plot = PredictionPlots(containers,week,day)
    prediction_plot.SetFillColorAlpha(ROOT.kBlack,0.4)
    plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),prediction_plot,'lE3')

    food_plot = GetDeltaBGversusTimePlot('food',containers,week,day)
    food_plot.SetFillStyle(3001)
    food_plot.SetFillColor(ROOT.kRed+1)
    food_plot.SetLineColor(ROOT.kRed+1)
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),food_plot,'lhist')

    insulin_plot = GetDeltaBGversusTimePlot('insulin',containers,week,day)
    insulin_plot.SetFillStyle(3001)
    insulin_plot.SetFillColor(ROOT.kGreen+1)
    insulin_plot.SetLineColor(ROOT.kGreen+1)
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),insulin_plot,'lhist')

    both_plot = GetDeltaBGversusTimePlot('insulin_food',containers,week,day)
    both_plot.SetFillStyle(3001)
    both_plot.SetLineWidth(2)
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),both_plot,'lhist')

    # Residual plot for sensor data
    if sensor_data.GetN() > 1 :
        residual_plot = ComparePredictionToReality(prediction_plot,sensor_data)
        residual_plot.SetMarkerSize(0.5)
        plotfunc.AddHistogram(plotfunc.GetBotPad(prediction_canvas),residual_plot,'p')

    # Residual plot for BG data
    residual_plot_2 = ComparePredictionToReality(bg_data,prediction_plot,reverse=True)
    residual_plot_2.SetMarkerSize(0.8)
    residual_plot_2.SetMarkerColor(ROOT.kRed+1)
    plotfunc.AddHistogram(plotfunc.GetBotPad(prediction_canvas),residual_plot_2,'p')

    ColorHistsAccordingToDay(prediction_canvas)
    for i in prediction_canvas.GetListOfPrimitives() :
        if 'SensorGlucose' in i.GetName() :
            i.SetMarkerSize(0.5)
            i.SetLineWidth(2)
    plotfunc.FormatCanvasAxes(prediction_canvas)
    taxisfunc.SetYaxisRanges(prediction_canvas,0.001,350)
    plotfunc.SetAxisLabels(prediction_canvas,'hr','BG (mg/dL)')

    taxisfunc.SetYaxisRanges(plotfunc.GetBotPad(prediction_canvas),-199,199)
    taxisfunc.SetXaxisRanges(plotfunc.GetBotPad(prediction_canvas),-0.5,24.5)

    taxisfunc.SetYaxisRanges(GetMidPad(prediction_canvas),-199,199)
    taxisfunc.SetXaxisRanges(GetMidPad(prediction_canvas),-0.5,24.5)
    taxisfunc.SetYaxisNdivisions(GetMidPad(prediction_canvas),5,5,0)
    GetMidPad(prediction_canvas).GetPrimitive('pad_mid_HistWithTimeAxis').GetXaxis().SetLabelOffset(5)
    GetMidPad(prediction_canvas).GetPrimitive('pad_mid_HistWithTimeAxis').GetYaxis().SetTitle('#Delta^{}BG^{ }/^{ }hr')
    plotfunc.GetBotPad(prediction_canvas).GetPrimitive('pad_bot_HistWithTimeAxis').GetXaxis().SetLabelOffset(.04)
    plotfunc.GetBotPad(prediction_canvas).GetPrimitive('pad_bot_HistWithTimeAxis').GetXaxis().SetTitleOffset(2.8)
    plotfunc.GetBotPad(prediction_canvas).GetPrimitive('pad_bot_HistWithTimeAxis').GetYaxis().SetTitle('data^{ }#minus^{ }pred')

    plotfunc.FormatCanvasAxes(prediction_canvas.GetPrimitive('pad_sub'))
    taxisfunc.SetYaxisRanges(prediction_canvas.GetPrimitive('pad_sub'),0.001,90)
    plotfunc.SetAxisLabels(prediction_canvas.GetPrimitive('pad_sub'),'','Settings')
    prediction_canvas.GetPrimitive('pad_sub').GetPrimitive('pad_sub_HistWithTimeAxis').GetXaxis().SetLabelOffset(10)
    prediction_canvas.GetPrimitive('pad_sub').GetPrimitive('pad_sub_HistWithTimeAxis').GetYaxis().SetNdivisions(5,2,0)

    #
    # Draw the date.
    #
    plotfunc.DrawText(prediction_canvas.GetPrimitive('pad_top'),
                      MyTime.StringFromTime(MyTime.DayWeekToUniversal(week,day),dayonly=True),
                      0.79,0.73,0.91,0.84,
                      totalentries=1
                      )

    #
    # Draw settings - insulin sensitivity
    #
    sensi_histograms = SettingsHistograms('Sensitivity')
    sensi_histograms.ReadFromFile(rootfile)

    # For now, just find the latest histogram
    hist_sensi = sensi_histograms.latestHistogram().Clone()
    hist_sensi.SetName('hist_sensi')
    hist_sensi.SetMarkerColor(ROOT.kGreen+1)
    hist_sensi.SetMarkerSize(0.2)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_sensi,'p')
    hist_sensi.SetMarkerSize(6)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_sensi,'text45')

    #
    # Draw settings - food sensitivity
    #
    ric_histograms = SettingsHistograms('RIC')
    ric_histograms.ReadFromFile(rootfile)
    hist_ric = ric_histograms.latestHistogram().Clone()
    hist_ric.SetName('hist_ric')
    hist_ric.SetMarkerColor(ROOT.kRed+1)
    hist_ric.SetMarkerSize(0.2)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_ric,'p')
    hist_ric.SetMarkerSize(6)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_ric,'text45')

    #
    # Draw settings - basal
    #
    basal_histograms = SettingsHistograms('Basal')
    basal_histograms.ReadFromFile(rootfile)
    hist_basal = basal_histograms.latestHistogram().Clone()
    hist_basal.SetName('hist_basal')
    hist_basal.SetMarkerColor(ROOT.kBlue+1)
    hist_basal.SetMarkerSize(0.2)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_basal,'p')
    hist_basal.SetMarkerSize(6)
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_basal,'text45')

    prediction_canvas.GetPrimitive('pad_sub').Modified()
    prediction_canvas.GetPrimitive('pad_sub').Update()
    GetMidPad(prediction_canvas).Modified()
    GetMidPad(prediction_canvas).Update()
    prediction_canvas.Modified()
    prediction_canvas.Update()
    return prediction_canvas

#------------------------------------------------------------------
def FindTimeOfNextBG(tree,i) :
    UT_next = MyTime.StartOfYear + MyTime.OneYear*1000. # end of 1000 years.
    for j in range(i+1,tree.GetEntries()) :
        tree.GetEntry(j)
        if tree.BGReading > 0 :
            UT_next = tree.UniversalTime
            break
    # Reset the tree to the entry we were at:
    tree.GetEntry(i)
    return UT_next

#------------------------------------------------------------------
def FindTimeAndBGOfPreviousBG(tree,i) :
    bg_read = 0
    UT_next = tree.UniversalTime
    for j in range(i-1,0,-1) :
        tree.GetEntry(j)
        if tree.BGReading > 0 :
            bg_read = tree.BGReading
            break
    tree.GetEntry(i)

    return UT_next,bg_read


#------------------------------------------------------------------
def GetDayContainers(tree,week,day) :

    print 'Called LoadDayEstimate'
    print '%%%%%%%%%%%%%%%%%%%'
    print ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day]
    print MyTime.StringFromTime(MyTime.WeekDayHourToUniversal(week,day,0))
    print '%%%%%%%%%%%%%%%%%%%'

    # The start of when we consider BG readings:
    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0)-MyTime.OneDay # from 4am

    # The start-time of relevant events is 6 hours before the first BG measurement (found below).
    # We consider earlier events because they can bleed into the next day.
    start_time_relevantEvents = 0

    # When to start printing out the bolus info to command-line
    start_printouts = MyTime.WeekDayHourToUniversal(week,day,0) - 6*MyTime.OneHour

    # The end-time - 4am the next day.
    end_time = MyTime.WeekDayHourToUniversal(week,day+1,0)

    containers = []

    #
    # BG Readings - get the LAST BG reading before the start of the plot-day (which we call "First BG")
    # This requires also finding the first BG reading, in order to get iov_1 for the first BG
    #
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)

        if tree.UniversalTime < start_of_plot_day :
            continue

        if tree.UniversalTime > end_time :
            continue

        if tree.BGReading > 0 :
            #
            # the iov_1 is the iov_0 of this first measurement
            #
            UT_next,bg_read = FindTimeAndBGOfPreviousBG(tree,i)

            # Make the "First BG" container entry:
            c = BGFunction('First BG', iov_0=tree.UniversalTime, iov_1=UT_next, const_BG=bg_read)
            containers.append(c)

            # Anything 6h before first measurement is a relevant event
            start_time_relevantEvents = tree.UniversalTime - 6.*MyTime.OneHour

            break
        #
    #

    #
    # Get the rest of the points
    #
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)

        if tree.UniversalTime < start_time_relevantEvents :
            continue

        if tree.UniversalTime > end_time :
            continue

        # Find BG readings
        if tree.BGReading > 0 and tree.UniversalTime > start_of_plot_day :

            # Make a BGReading container
            c = BGFunction('BGReading', iov_0=tree.UniversalTime, const_BG=tree.BGReading)
            c.iov_1 = FindTimeOfNextBG(tree,i)

            # Add the BG reading to the list
            containers.append(c)


        # Insulin
        if tree.BolusVolumeDelivered > 0 :

            c = BGFunction('Insulin',Ta=4,I0Est=0,S=60)
            c.iov_0 = tree.UniversalTime
            c.iov_1 = c.iov_0 + 6.*MyTime.OneHour
            c.I0    = tree.BolusVolumeDelivered
            c.S     = 60. # need to fix!

            # Matching BWZEstimate from delivered insulin
            IsBWZEstimate = False

            # Try to find (within 5 seconds) the bolus wizard estimate
            for j in range(i-1,i-10,-1) + range(i+1,i+10) :
                tree.GetEntry(j)
                if tree.BWZEstimate > 0 and (abs(tree.UniversalTime - c.iov_0) < 5*MyTime.OneSecond) :
                    c.I0Est = tree.BWZEstimate
                    c.S     = tree.BWZInsulinSensitivity
                    c.BWZCorrectionEstimate = tree.BWZCorrectionEstimate
                    c.BWZFoodEstimate       = tree.BWZFoodEstimate
                    c.BWZActiveInsulin      = tree.BWZActiveInsulin
                    c.BWZBGInput            = tree.BWZBGInput
                    c.RIC                   = tree.BWZCarbRatio
                    IsBWZEstimate = True
                    break

            # Reset tree entry
            tree.GetEntry(i)

            if not IsBWZEstimate :
                print 'Warning! Could not find BWZ estimate!',MyTime.StringFromTime(c.iov_0)

            if IsBWZEstimate and (c.I0 != c.I0Est) :
                c.BWZMatchedDelivered = False

            if c.iov_0 > start_printouts :
                c.PrintBolus()

            containers.append(c)

        #
        # Food
        #
        if tree.BWZCarbInput > 0 :

            c = BGFunction('Food',Ta=2)
            c.iov_0 = tree.UniversalTime
            c.iov_1 = tree.UniversalTime+6.*MyTime.OneHour
            c.S     = tree.BWZInsulinSensitivity
            c.C   = tree.BWZCarbInput
            c.RIC = tree.BWZCarbRatio

            # starting on March 25, 2015:
            if tree.UniversalTime > MyTime.TimeFromString('03/25/15 10:00:00') :
                add_time = (tree.BWZCarbInput % 5)
                #print 'Grading based on %5.',
                #print 'Food was %d. New decay time: %2.1f.'%(tree.BWZCarbInput,2. + add_time)
                c.Ta = 2. + add_time

            containers.append(c)

    #
    # Now make the prediction plots (moved elsewhere)
    #
    return containers

#------------------------------------------------------------------
def ComparePredictionToReality(prediction,reality,reverse=False) :
    from array import array
    import math

    x_real = reality.GetX()
    y_real = reality.GetY()

    x_pred = prediction.GetX()
    y_pred = prediction.GetY()
    
    x_diff = []
    y_diff = []

    for xp in range(prediction.GetN()) :
        not_yet = True
        for xr in range(reality.GetN()) :
            if not_yet and math.fabs(x_pred[xp] - x_real[xr]) < 1./6. :
                x_diff.append(x_pred[xp])
                factor = -1. if reverse else 1.
                y_diff.append((y_real[xr] - y_pred[xp])*factor)
                not_yet = False
            if not not_yet :
                break

    h = ROOT.TGraph(len(x_diff),array('d',x_diff),array('d',y_diff))
    h.SetName('Compare_prediction_to_reality')
    return h

#------------------------------------------------------------------
def GetDeltaBGversusTimePlot(the_type,containers,week,day) :
    #
    # Plot the deltaBG per hour. Because it is per hour, and plotted versus hour, the integral
    # is the total dose.
    #

    import math
    import ROOT

    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0) # from 4am
    hours_per_step = 0.1

    h = ROOT.TH1F('%d_%d_%s'%(week,day,the_type),'asdf',int(24./hours_per_step),-0.5,24.5)

    for i in range(int(24./hours_per_step)+1) :
        the_time = start_of_plot_day + i*hours_per_step*float(MyTime.OneHour) # universal
        for c in containers :
            if the_time < c.iov_0 :
                continue
            if c.C and 'food' in the_type :
                h.AddBinContent(i+1,c.getBGImpactDerivPerHour(the_time))
            if c.I0 and 'insulin' in the_type :
                h.AddBinContent(i+1,c.getBGImpactDerivPerHour(the_time))
    return h

#------------------------------------------------------------------
def PredictionPlots(containers,week,day,constant_ref=-1,RIC_n_up=2,RIC_n_dn=-2) :
    # NEED TO FIX RIC STUFF!
    #
    # The standard prediction plot.
    # Returns one plot, for one day, with the predicted BG curve.
    # Week and day figure into the start_of_plot_day
    # but probably they can be removed with some small effort
    #
    import math

    # Start of the daily plot, from 4am
    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0) # from 4am

    # Granularity of the prediction
    hours_per_step = 0.2

    prediction_graph = ROOT.TGraph()
    prediction_graph.SetTitle('prediction')

    bg_estimates = []

#     for c in containers :
#         c.Print()

    # When we hit a BG reading, then we want to consider (once) resetting the prediction.
    considered_for_bgReset = []

    for i in range(int(24./hours_per_step)) :

        the_time = start_of_plot_day + i*hours_per_step*float(MyTime.OneHour) # universal
        time_on_plot = hours_per_step*i

        # We start the estimate with the estimate from the previous point.
        # We will calculate the differential effect of each object.
        # The effects are assumed to be additive.
        # If this is the first point, then we will
        bg_estimates.append( 0 if (not i) else bg_estimates[-1] )

        # We'll keep track of whether large boluses are in progress in this time-step
        max_bgEffectRemaining = 0

        #
        # Quick function to find the first BG
        #
        def findFirstBG(conts) :
            for c in conts :
                if c.type == 'First BG' :
                    return c
            return None

        for c in containers :

            if the_time < c.iov_0 :
                continue

            # Special treatment for the first bin of the day:
            if (i==0) and (c.I0 or c.C) :

                # Find the first BG
                first_bg_time = findFirstBG(containers).iov_0
                integral = c.getIntegral(the_time) - c.getIntegral(first_bg_time)
                bg_estimates[-1] += integral
                continue

            # If the object time has expired, skip it.
            if the_time > c.iov_1 :
                continue

            # For the typical bin in the day-plot:
            if c.I0 or c.C :
                impactInTimeInterval = c.getBGImpactDerivTimesInterval(the_time,hours_per_step)
                bg_estimates[-1] += impactInTimeInterval
                max_bgEffectRemaining = max(max_bgEffectRemaining,math.fabs(c.bgImpactRemaining(the_time)))

            # If there was a new reading, we reset the prediction (with the caveats below)
            if c.const_BG and not (c.iov_0 in considered_for_bgReset) :

                # We should only consider resetting one time!
                considered_for_bgReset.append(c.iov_0)

                # If nothing is in progress that would cause 30 points drop/increase,
                # reset the prediction.
                if max_bgEffectRemaining < 30 :
                    bg_estimates[-1] = c.const_BG

        # end loop over containers

        # add a new point to the graph
        prediction_graph.SetPoint(prediction_graph.GetN(),time_on_plot,bg_estimates[-1])

    return prediction_graph
