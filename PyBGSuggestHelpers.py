import time
from array import array
import ROOT

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
            # Tidepool format
            return long(time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%S')))
    
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
    def __init__(self) :
        self.type = 'Unknown'
        self.iov_0 = 0 # universal time - start of interval of validity
        self.iov_1 = 0 # universal time - end of interval of validity
        self.const_BG = 0 # 
        self.S = 0 # sensitivity
        self.Ta = 4. # active insulin time
        self.I0Est = 0.
        self.I0 = 0.
        self.C = 0. # carb input
        self.RIC = 0.
        self.Registered = None
        #
        self.BWZCorrectionEstimate = 0.
        self.BWZFoodEstimate = 0.
        self.BWZActiveInsulin = 0.
        self.BWZBGInput = 0.
        self.BWZMatchedDelivered = True
        self.t = TimeClass()
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
        #
        #
        import math
        if time < self.iov_0 : return 0.
        #if time > self.iov_1 : return 0.
        
        time_hr = (time-self.iov_0)/float(self.t.OneHour)
        
        result = 1
        result -= math.pow(0.05,math.pow(time_hr/self.Ta,2))
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
        #print 'returning result',result
        return result

    def stuffRemaining(self,time,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        
        return (self.getIntegral(time,S_fac,C_fac,RIC_fac,RIC_n) -
                self.getIntegral(time*1000,S_fac,C_fac,RIC_fac,RIC_n)) # "infinity"

    def getDDX(self,time,delta,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        import math
        #time += delta
        if time < self.iov_0 : return 0.
        if time > self.iov_1 : return 0.

        time_hr = (time-self.iov_0)/float(self.t.OneHour)
        
        result = 2*math.pow((1/self.Ta),2)
        result *= 3.0 # ln 20
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
        result *= time_hr
        result *= math.pow(0.05,math.pow(time_hr/self.Ta,2))
        #result *= (time_hr < 6)
        result *= delta
        #print 'returning result',result
        return result

    def getDDXtimesInterval(self,time,delta,S_fac=1.,C_fac=1.,RIC_fac=1.,RIC_n=0.) :
        import math
        #time += delta
        if time < self.iov_0 : return 0.
        if time > self.iov_1 : return 0.

        time_hr = (time-self.iov_0)/float(self.t.OneHour)
        
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
        print 'iov_0',self.iov_0,self.t.StringFromTime(self.iov_0)
        print 'iov_1',self.iov_1,self.t.StringFromTime(self.iov_1)
        print 'BG   ',self.const_BG
        print 'S    ',self.S    
        print 'Ta   ',self.Ta   
        print 'I0   ',self.I0
        print 'Reg  ',self.Registered

        return

    def PrintBolus(self) :
        s = self.S
        f = self.RIC
        star = ' *' if not self.BWZMatchedDelivered else ''
        print 'Bolus, %s (input BG: %d mg/dl) (S=%d)'%(self.t.StringFromTime(self.iov_0),self.BWZBGInput,s)
        print '  Total Delivered BS : %2.1f u;'%(self.I0                   )+(' %2.1f mg/dl'%(self.I0                   *s)).rjust(15)+(' %2.1f g'%(self.I0                   *f)).rjust(15)+star
        print '  Total Suggested BS : %2.1f u;'%(self.I0Est                )+(' %2.1f mg/dl'%(self.I0Est                *s)).rjust(15)+(' %2.1f g'%(self.I0Est                *f)).rjust(15)
        print '                food : %2.1f u;'%(self.BWZFoodEstimate      )+(' %2.1f mg/dl'%(self.BWZFoodEstimate      *s)).rjust(15)+(' %2.1f g'%(self.BWZFoodEstimate      *f)).rjust(15)
        print '          correction : %2.1f u;'%(self.BWZCorrectionEstimate)+(' %2.1f mg/dl'%(self.BWZCorrectionEstimate*s)).rjust(15)+(' %2.1f g'%(self.BWZCorrectionEstimate*f)).rjust(15)
        print '              active : %2.1f u;'%(self.BWZActiveInsulin     )+(' %2.1f mg/dl'%(self.BWZActiveInsulin     *s)).rjust(15)+(' %2.1f g'%(self.BWZActiveInsulin     *f)).rjust(15)
        #print UNIXcolor.BOLD + 'Hello World !' + color.END
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

    #prediction_canvas = ThreePadCanvas('prediction_canvas','prediction_canvas',600,500)
    prediction_canvas = ThreePadCanvas('prediction_canvas','prediction_canvas',600,600,
                                       ratio_1=0.41,
                                       ratio_2=0.59,
                                       ratio_n1=0.17
                                       )
    #prediction_canvas.SetWindowSize(500,500)
    week = GetLastWeek(tree)
    week = week - weeks_ago
    
    plotfunc.AddHistogram(prediction_canvas,GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(plotfunc.GetBotPad(prediction_canvas),GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),GetHistWithTimeAxis(),'')
    plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),GetHistWithTimeAxis(),'')

    band = ROOT.TH1F('band','skipme',1,-0.5,24.5)
    band.SetBinContent(1,130)
    band.SetBinError(1,50)
    band.SetFillColor(ROOT.kOrange-0)
    band.SetMarkerSize(0)

    band2 = ROOT.TH1F('band2','skipme',1,-0.5,24.5)
    band2.SetBinContent(1,125)
    band2.SetBinError(1,25)
    band2.SetFillColor(ROOT.kGreen-0)
    band2.SetMarkerSize(0)

    plotfunc.AddHistogram(prediction_canvas,band,'E2')
    plotfunc.AddHistogram(prediction_canvas,band2,'E2')
    plotfunc.GetTopPad(prediction_canvas).RedrawAxis()

    sensor_data = GetDataFromDay(tree,'SensorGlucose',day,week)
    sensor_data.SetMarkerSize(0.7)
    if sensor_data.GetN() > 1 :
        plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),sensor_data,'p')

    bg_data = GetDataFromDay(tree,'BGReading',day,week)
    bg_data.SetMarkerColor(ROOT.kRed+1)
    plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),bg_data,'p')

    containers = GetDayContainers(tree,week,day)
    prediction_plot = PredictionPlots(containers,week,day)
    prediction_plot.SetFillStyle(3001)
    plotfunc.AddHistogram(plotfunc.GetTopPad(prediction_canvas),prediction_plot,'lE3')

    food_plot = DDX('food',containers,week,day)
    food_plot.SetFillStyle(3001)
    food_plot.SetFillColor(ROOT.kRed+1)
    food_plot.SetLineColor(ROOT.kRed+1)
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),food_plot,'lhist')

    insulin_plot = DDX('insulin',containers,week,day)
    insulin_plot.SetFillStyle(3001)
    insulin_plot.SetFillColor(ROOT.kGreen+1)
    insulin_plot.SetLineColor(ROOT.kGreen+1)
    plotfunc.AddHistogram(GetMidPad(prediction_canvas),insulin_plot,'lhist')

    both_plot = DDX('insulin_food',containers,week,day)
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
    t = TimeClass()
    plotfunc.DrawText(prediction_canvas.GetPrimitive('pad_top'),
                      t.StringFromTime(t.DayWeekToUniversal(week,day),dayonly=True),
                      0.79,0.73,0.91,0.84,
                      totalentries=1
                      )

    #
    # Draw settings - insulin sensitivity
    #
    if rootfile :
        hist_sensi = None
        for i in rootfile.GetListOfKeys() :
            if 'Sensitivity' not in i.GetName() :
                continue
            #print i.GetName()
            #print 'day of week is',t.GetDayOfWeek(time_in_question)
            if t.DayWeekToUniversal(week,day) > t.TimeFromString(i.GetName().replace('Sensitivity ','')) :
                #print 'Stopping at',i.GetName()
                hist_sensi = i.ReadObj()
                hist_sensi.SetMarkerColor(ROOT.kGreen+1)
                hist_sensi.SetMarkerSize(0.2)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_sensi,'p')
                hist_sensi.SetMarkerSize(6)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_sensi,'text45')
                break

    #
    # Draw settings - food sensitivity
    #
    if rootfile :
        hist_foodsensi = None
        for i in rootfile.GetListOfKeys() :
            if 'RIC' not in i.GetName() :
                continue
            #print i.GetName()
            #print 'day of week is',t.GetDayOfWeek(time_in_question)
            if t.DayWeekToUniversal(week,day) > t.TimeFromString(i.GetName().replace('RIC ','')) :
                #print 'Stopping at',i.GetName()
                hist_foodsensi = i.ReadObj()
                hist_foodsensi.SetMarkerSize(0.2)
                hist_foodsensi.SetMarkerColor(ROOT.kRed+1)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_foodsensi,'p')
                hist_foodsensi.SetMarkerSize(6)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_foodsensi,'text45')
                break

    #
    # Draw settings - basal
    #
    if rootfile :
        hist_basalsensi = None
        for i in rootfile.GetListOfKeys() :
            if 'Basal' not in i.GetName() :
                continue
            #print i.GetName()
            #print 'day of week is',t.GetDayOfWeek(time_in_question)
            if t.DayWeekToUniversal(week,day) > t.TimeFromString(i.GetName().replace('Basal ','')) :
                #print 'Stopping at',i.GetName()
                hist_basalsensi = i.ReadObj()
                hist_basalsensi.SetMarkerSize(0.2)
                hist_basalsensi.SetMarkerColor(ROOT.kBlue+1)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_basalsensi,'p')
                hist_basalsensi.SetMarkerSize(6)
                plotfunc.AddHistogram(prediction_canvas.GetPrimitive('pad_sub'),hist_basalsensi,'text45')
                break

    prediction_canvas.GetPrimitive('pad_sub').Modified()
    prediction_canvas.GetPrimitive('pad_sub').Update()
    GetMidPad(prediction_canvas).Modified()
    GetMidPad(prediction_canvas).Update()
    prediction_canvas.Modified()
    prediction_canvas.Update()
    return prediction_canvas

#------------------------------------------------------------------
def GetDayContainers(tree,week,day) :
    t = TimeClass()
    print 'Called LoadDayEstimate'
    print '%%%%%%%%%%%%%%%%%%%'
    print ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day]
    print t.StringFromTime(t.WeekDayHourToUniversal(week,day,0))
    print '%%%%%%%%%%%%%%%%%%%'

    #
    # Look for any event between midnight of the previous day and 4am of the next day.
    #
    #self.start_time = t.WeekDayHourToUniversal(week,day,0)  # idk
    #print 'self.start_time DDX', self.start_time
    #start_time_rr = self.start_time                          # relevant readings - will change

    start_of_plot_day = t.WeekDayHourToUniversal(week,day,0)-t.OneDay # from 4am
    end_time = t.WeekDayHourToUniversal(week,day+1,0)   # events ending at 4am

    containers = []

    #
    # BG Readings - get carry-over.
    #
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        if tree.UniversalTime < start_of_plot_day : continue
        if tree.UniversalTime > end_time : continue
        if tree.BGReading > 0 :
            #
            # the iov_1 is the iov_0 of this first measurement
            #
            bg_read = 0
            UT_next = tree.UniversalTime
            for j in range(i-1,0,-1) :
                tree.GetEntry(j)
                if tree.BGReading > 0 :
                    bg_read = tree.BGReading
                    break

            containers.append(BGFunction())
            containers[-1].iov_0 = tree.UniversalTime
            containers[-1].type = 'First BG'
            start_time_rr = tree.UniversalTime - 6.*t.OneHour # start collecting 6h before first meas.
            containers[-1].const_BG = bg_read
            containers[-1].iov_1 = UT_next


            break
        #
    #

    #
    # Get the rest of the points
    #
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        #print 'time',t.StringFromTime(tree.UniversalTime),'BG',tree.BGReading
        if tree.UniversalTime < start_time_rr : continue
        #
        # Should not need this
        #
        #if tree.UniversalTime < self.start_of_plot_day and tree.BGReading > 0 : continue # skip earlier meas.
        if tree.UniversalTime > end_time : continue

        if tree.BGReading > 0 and tree.UniversalTime > start_of_plot_day :
            containers.append(BGFunction())
            containers[-1].type = 'BGReading'
            containers[-1].const_BG = tree.BGReading
            containers[-1].iov_0 = tree.UniversalTime

            #
            # find next meas
            #
            UT_next = t.StartOfYear + t.OneYear*1000. # end of 1000 years.
            for j in range(i+1,tree.GetEntries()) :
                tree.GetEntry(j)
                if tree.BGReading > 0 :
                    #print 'Previous BG was: %d Next BG Reading is: %d'%(containers[-1].const_BG,tree.BGReading)
                    UT_next = tree.UniversalTime
                    break
            containers[-1].iov_1 = UT_next
            tree.GetEntry(i)

        #
        # Insulin mothafucka
        #
        if tree.BolusVolumeDelivered > 0 :

            containers.append(BGFunction())
            containers[-1].type  = 'Insulin'
            containers[-1].iov_0 = tree.UniversalTime
            containers[-1].iov_1 = tree.UniversalTime+6.*t.OneHour
            containers[-1].Ta    = 4.
            containers[-1].I0    = tree.BolusVolumeDelivered
            containers[-1].I0Est = 0.
            containers[-1].S     = 60. # need to fix!

            #
            # Matching BWZEstimate from delivered insulin
            #
            IsBWZEstimate = False
            for j in range(i-1,i-10,-1) :
                tree.GetEntry(j)
                if tree.BWZEstimate > 0 and (abs(tree.UniversalTime - containers[-1].iov_0)<5) :
                    containers[-1].I0Est = tree.BWZEstimate
                    containers[-1].S     = tree.BWZInsulinSensitivity
                    containers[-1].BWZCorrectionEstimate = tree.BWZCorrectionEstimate
                    containers[-1].BWZFoodEstimate       = tree.BWZFoodEstimate      
                    containers[-1].BWZActiveInsulin      = tree.BWZActiveInsulin     
                    containers[-1].BWZBGInput            = tree.BWZBGInput
                    containers[-1].RIC                   = tree.BWZCarbRatio
                    IsBWZEstimate = True
                    break
                #if j == i-9 :
                #    print 'Warning! Could not find BWZ estimate!',t.StringFromTime(containers[-1].iov_0)
            for j in range(i+1,i+10) :
                if containers[-1].I0Est > 0 : 
                    break
                tree.GetEntry(j)
                if tree.BWZEstimate > 0 and (abs(tree.UniversalTime - containers[-1].iov_0)<5) :
                    containers[-1].I0Est = tree.BWZEstimate
                    containers[-1].S     = tree.BWZInsulinSensitivity
                    containers[-1].BWZCorrectionEstimate = tree.BWZCorrectionEstimate
                    containers[-1].BWZFoodEstimate       = tree.BWZFoodEstimate      
                    containers[-1].BWZActiveInsulin      = tree.BWZActiveInsulin     
                    containers[-1].BWZBGInput            = tree.BWZBGInput
                    containers[-1].RIC                   = tree.BWZCarbRatio
                    IsBWZEstimate = True
                    break
                if j == i+9 :
                    print 'Warning! Could not find BWZ estimate!',t.StringFromTime(containers[-1].iov_0)

            if IsBWZEstimate and (containers[-1].I0 != containers[-1].I0Est) :
                containers[-1].BWZMatchedDelivered = False
                #print 'Estimate != delivered!',
                #print t.StringFromTime(containers[-1].iov_0),
                #diff = 100.*(containers[-1].I0-containers[-1].I0Est)/float(containers[-1].I0Est)
                #print '%2.1f Est, %2.1f delivered. %2.1f'%(containers[-1].I0Est,containers[-1].I0,diff)+'%'

            if containers[-1].iov_0 > start_of_plot_day :
                containers[-1].PrintBolus()

            tree.GetEntry(i)
        #
        # Food bitch!
        #
        if j != i : 
            j = i
        tree.GetEntry(i)
        if tree.BWZCarbInput > 0 :

            containers.append(BGFunction())
            containers[-1].type  = 'Food'
            containers[-1].iov_0 = tree.UniversalTime
            containers[-1].iov_1 = tree.UniversalTime+6.*t.OneHour
            containers[-1].S     = tree.BWZInsulinSensitivity
            containers[-1].Ta    = 2.
            # starting on March 25,
            if tree.UniversalTime > t.TimeFromString('03/25/15 10:00:00') :
                add_time = (tree.BWZCarbInput % 5)
                print 'Grading based on %5.',
                print 'Food was %d. New decay time: %2.1f.'%(tree.BWZCarbInput,2. + add_time)
                containers[-1].Ta    = 2. + add_time
            containers[-1].C     = tree.BWZCarbInput
            containers[-1].RIC   = tree.BWZCarbRatio

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
def DDX(the_type,containers,week,day,constant_ref=-1,RIC_n_up=-1,RIC_n_dn=1) :
    import math
    import ROOT
    t = TimeClass()

    start_of_plot_day = t.WeekDayHourToUniversal(week,day,0) # from 4am
    hours_per_step = 0.1
    x_time = []
    y_bg = []

    h = ROOT.TH1F('%d_%d_%s'%(week,day,the_type),'asdf',int(24./hours_per_step),-0.5,24.5)
    h.SetBinContent(0,0)
    h.SetBinContent(h.GetNbinsX()+1,0)
    for i in range(int(24./hours_per_step)+1) :
        the_time = start_of_plot_day + i*hours_per_step*float(t.OneHour) # universal
        for c in containers :
            if the_time < c.iov_0 : continue
            if c.C and 'food' in the_type :
                h.AddBinContent(i+1,c.getDDX(the_time,hours_per_step) / float(hours_per_step))
            if c.I0 and 'insulin' in the_type :
                h.AddBinContent(i+1,c.getDDX(the_time,hours_per_step) / float(hours_per_step))
    return h

#------------------------------------------------------------------
def PredictionPlots(containers,week,day,constant_ref=-1,RIC_n_up=-1,RIC_n_dn=1) :
    #
    # The standard prediction plots for week
    # Returns one plot, for one day, with the predicted levels.
    # Week and day figure into the start_of_plot_day
    # but probably they can be removed with some small effort
    #
    import math
    t = TimeClass()

    start_of_plot_day = t.WeekDayHourToUniversal(week,day,0) # from 4am
    hours_per_step = .2
    x_time = []
    y_bg = []
    y_bg_err_up = []
    y_bg_err_dn = []

#     for c in containers :
#         c.Print()

    for i in range(int(24./hours_per_step)) :
        the_time = start_of_plot_day + i*hours_per_step*float(t.OneHour) # universal

        # HACK if it's not lining up (daylight savings time for instance)
        x_time.append(0+hours_per_step*i)
        if len(y_bg) : 
            y_bg.append(y_bg[-1])
            y_bg_err_up.append(y_bg_err_up[-1])
            y_bg_err_dn.append(y_bg_err_dn[-1])
        else : 
            y_bg.append(0)
            y_bg_err_up.append(0)
            y_bg_err_dn.append(0)

        #
        # We'll keep track of whether large boluses are in progress
        #
        max_action = 0

        #
        # Find the last measurement time
        #
        last_meas_time = the_time
        for c in containers :
            if c.type == 'First BG' :
                last_meas_time = c.iov_0
                break

        for c in containers :

            if the_time < c.iov_0 : continue

            #
            # For the first entry of the day:
            #
            if (i==0) and (c.I0 or c.C) :
                nom_integral = c.getIntegral(the_time            ) - c.getIntegral(last_meas_time            )
                # up_integral  = c.getIntegral(the_time,RIC_fac=self.RIC_fac_up) - c.getIntegral(last_meas_time,RIC_fac=self.RIC_fac_up)
                # dn_integral  = c.getIntegral(the_time,RIC_fac=self.RIC_fac_dn) - c.getIntegral(last_meas_time,RIC_fac=self.RIC_fac_dn)
                up_integral  = c.getIntegral(the_time,RIC_n=RIC_n_up) - c.getIntegral(last_meas_time,RIC_n=RIC_n_up)
                dn_integral  = c.getIntegral(the_time,RIC_n=RIC_n_dn) - c.getIntegral(last_meas_time,RIC_n=RIC_n_dn)
                y_bg[-1] += nom_integral
                y_bg_err_up[-1] += up_integral - nom_integral
                y_bg_err_dn[-1] += nom_integral - dn_integral
                continue

            if the_time > c.iov_1 : continue

            #
            # For the nominal entry
            #
            if c.I0 or c.C :
                nom_ddx = c.getDDXtimesInterval(the_time,hours_per_step)
                up_ddx = c.getDDXtimesInterval(the_time,hours_per_step,RIC_n=RIC_n_up)
                dn_ddx = c.getDDXtimesInterval(the_time,hours_per_step,RIC_n=RIC_n_dn)
                y_bg[-1] += nom_ddx
                y_bg_err_up[-1] += up_ddx - nom_ddx
                y_bg_err_dn[-1] += nom_ddx - dn_ddx
                max_action = max(max_action,math.fabs(c.stuffRemaining(the_time)))
            #
            # If there was a new reading, we reset the prediction... if...
            #
            if c.const_BG and not c.Registered : 
                c.Registered = True
                #
                # If something is in progress that would cause 30 points drop/increase,
                # skip the recalibration.
                #
                if max_action < 30 :
                    y_bg[-1] = c.const_BG
                    y_bg_err_up[-1] = 0.
                    y_bg_err_dn[-1] = 0.

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

    myddx = ROOT.TGraphAsymmErrors(len(x_time)-1,x_time_d,y_bg_d,
                                   x_bg_d_err_up,x_bg_d_err_dn,y_bg_d_err_up,y_bg_d_err_dn)

    return myddx
