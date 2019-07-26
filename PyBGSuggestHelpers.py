from array import array
import ROOT
from TimeClass import MyTime
from Settings import SettingsHistograms,TrueUserProfile
from BGActionClasses import BGMeasurement,InsulinBolus,Food,LiverBasalGlucose,BasalInsulin,findFirstBG
from BGActionClasses import TempBasal,Suspend,ExerciseEffect,Annotation,SquareWaveBolus,LiverFattyGlucose
import Fitting
import copy
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
import PlotManagement

positive_bg_items = ['Food','LiverFattyGlucose','LiverBasalGlucose']
negative_bg_items = ['InsulinBolus','BasalInsulin','ExerciseEffect','SquareWaveBolus']

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

        if time < self.iov_0 :
            return 0.
        
        time_hr = (time-self.iov_0)/float(MyTime.OneHour)
        
        result = 1
        result -= math.pow(0.05,math.pow(time_hr/float(self.Ta),2))
        result *= self.getEffectiveSensitivity(S_fac=S_fac,C_fac=C_fac,RIC_fac=RIC_fac,RIC_n=RIC_n)
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
def GetLastWeek(tree) :
    last_week = 0
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        last_week = max(last_week,tree.WeekOfYear)
    return last_week

#------------------------------------------------------------------
def DrawEventDetails(containers,start_of_day,can,settings) :
    from PlotFunctions import tobject_collector

    can.cd()

    BGSTART = 225
    BGO = 40
    bgoffset_upper = BGO
    bgoffset_lower = BGO
    hr_tracker_upper = 0
    hr_tracker_lower = 0

    for c in containers :

        if not (c.IsBolus() or c.IsFood() or c.IsSuspend() or c.IsExercise()) :
            continue

        if c.iov_0 < start_of_day :
            continue

        t = ROOT.TLatex((c.iov_0 - start_of_day)/float(MyTime.OneHour),-BGSTART,'.')
        t.SetName('%s %s'%(c.__class__.__name__, MyTime.StringFromTime(c.iov_0)))
        t.SetTextFont(43)
        t.SetTextSize(10)
        t.SetTextAlign(12)

        if c.IsBolus() or (c.IsSuspend() and c.Duration_hr() > 0.1) or c.IsExercise() :

            if c.IsSuspend() :
                t.SetTitle('.OFF %2.1fhr'%(c.Duration_hr()))

            if c.IsExercise() :
                t.SetTitle('#times%.1f (#minus%.0f)'%(c.factor+1,-c.getMagnitudeOfBGEffect(settings)))

            if c.IsBolus() :
                t.SetTitle('%.1fu (#minus%.0f)'%(c.insulin,-c.getMagnitudeOfBGEffect(settings)))

            # Figure out where to put it
            t.SetY(-BGSTART)
            if (c.iov_0-hr_tracker_lower) < 3.1*MyTime.OneHour :
                t.SetY(t.GetY() + bgoffset_lower)
                bgoffset_lower += BGO
            else :
                hr_tracker_lower = c.iov_0
                bgoffset_lower = BGO

        if c.IsFood() :

            if c.IsFood() :
                t.SetTitle('%.0fg (+%.0f)'%(c.food,c.getMagnitudeOfBGEffect(settings)))

            # Figure out where to put it
            t.SetY(BGSTART)
            if (c.iov_0-hr_tracker_upper) < 3.1*MyTime.OneHour :
                t.SetY(t.GetY() - bgoffset_upper)
                bgoffset_upper += BGO
            else :
                hr_tracker_upper = c.iov_0
                bgoffset_upper = BGO

        t.Draw()
        tobject_collector.append(t)

    return

#------------------------------------------------------------------
def PredictionCanvas(tree,day,weeks_ago=0,rootfile=0) :
    print 'Calculating the prediction from day-of-week %d of %d weeks ago'%(day,weeks_ago)
    from array import array

    nHours = 32
    doResidualAndSettings = False

    if doResidualAndSettings :
        prediction_canvas = PlotManagement.ThreePadCanvas('prediction_canvas','prediction_canvas',600,600,
                                                          ratio_1=0.41,
                                                          ratio_2=0.59,
                                                          ratio_n1=0.17
                                                          )

        PlotManagement.FormatThreePadCanvas(prediction_canvas,nHours)
        residual_canvas = plotfunc.GetBotPad(prediction_canvas)
        settings_canvas = prediction_canvas.GetPrimitive('pad_sub')
        delta_canvas = prediction_canvas.GetPrimitive('pad_mid')

    else :
        prediction_canvas = plotfunc.RatioCanvas('prediction_canvas','prediction_canvas',600,500,0.5)
        delta_canvas = prediction_canvas.GetPrimitive('pad_bot')
        residual_canvas = None # plotfunc.GetBotPad(prediction_canvas)
        settings_canvas = None # prediction_canvas.GetPrimitive('pad_sub')

        PlotManagement.FormatBGCanvas(prediction_canvas,nHours=nHours)
        PlotManagement.FormatDeltaCanvas(delta_canvas,nHours=nHours)

    bg_canvas = plotfunc.GetTopPad(prediction_canvas)

    week = GetLastWeek(tree)
    week = week - weeks_ago

    # Sensor data (if available)
    sensor_data = GetDataFromDay(tree,'SensorGlucose',day,week)
    sensor_data.SetMarkerSize(0.5)
    sensor_data.SetLineWidth(2)
    if sensor_data.GetN() > 1 :
        plotfunc.AddHistogram(bg_canvas,sensor_data,'p')

    containers = GetDayContainers(tree,week,day,nHours=nHours)

    # BG data
    bg_data = ROOT.TGraph()
    for c in containers :
        if c.IsMeasurement() :
            time_from_start = (c.iov_0 - MyTime.WeekDayHourToUniversal(week,day,0))/float(MyTime.OneHour)
            bg_data.SetPoint(bg_data.GetN(),time_from_start,c.const_BG)

    bg_data.SetMarkerColor(ROOT.kRed+1)
    bg_data.SetTitle('remove')
    plotfunc.AddHistogram(bg_canvas,bg_data,'p')

    containers.append(LiverBasalGlucose())

    #
    # Get settings - insulin sensitivity, RIC, Basal
    #
    sensi_histograms = SettingsHistograms('Sensitivity')
    sensi_histograms.ReadFromFile(rootfile)

    ric_histograms = SettingsHistograms('RIC')
    ric_histograms.ReadFromFile(rootfile)

    basal_histograms = SettingsHistograms('Basal')
    basal_histograms.ReadFromFile(rootfile)

    duration_histograms = SettingsHistograms('Duration')
    duration_histograms.ReadFromFile(rootfile)

    # basal
    basal = BasalInsulin(findFirstBG(containers).iov_0 - 6*MyTime.OneHour,
                         MyTime.WeekDayHourToUniversal(week,day,nHours),
                         basal_histograms.latestHistogram(),
                         sensi_histograms.latestHistogram(),
                         containers)
    containers.append(basal)

    # Sort again to put the temp BasalGlucose in order:
    def MyFn(c) :
        return c.iov_0
    containers = sorted(containers,key=MyFn)

    # Load exercise stuff:
    for c in containers :
        if c.IsExercise() :
            c.LoadContainers(containers)

    # basal, normal schedule
    basal_schedule = BasalInsulin(findFirstBG(containers).iov_0 - 6*MyTime.OneHour,
                                  MyTime.WeekDayHourToUniversal(week,day,nHours),
                                  basal_histograms.latestHistogram())

    #
    # Make BolusWizard UserProfile
    #
    bwzProfile = TrueUserProfile()
    bwzProfile.AddSensitivityFromHistograms(sensi_histograms.latestHistogram(),
                                            ric_histograms.latestHistogram())
    bwzProfile.AddHourlyGlucoseFromHistogram(basal_histograms.latestHistogram(),
                                             duration_histograms.latestHistogram())
    bwzProfile.AddDurationFromHistogram(duration_histograms.latestHistogram())

    # Make the prediction plot (including error bars)
    prediction_plot = PredictionPlots(containers,bwzProfile,week,day,nHours=nHours)
    prediction_plot.SetTitle("Bolus Wizard prediction")
    prediction_plot.SetFillColorAlpha(ROOT.kBlack,0.4)
    prediction_plot.SetLineWidth(2)
    prediction_plot.SetLineStyle(7)
    plotfunc.AddHistogram(bg_canvas,prediction_plot,'lE3')

    #
    # Experimental profile: Make a deep copy of original profile
    #
    experimentalProfile = copy.deepcopy(bwzProfile)
    # Change food from 17h to 22h to 3.4
    for i in range(17*2,22*2) :
        experimentalProfile.setFoodSensitivityHrMidnight(i/2.,3.4)
    experimentalPlot = PredictionPlots(containers,experimentalProfile,week,day,nHours=nHours)
    experimentalPlot.SetLineColor(ROOT.kRed)
    experimentalPlot.SetLineWidth(2)
    experimentalPlot.SetTitle("Experimenatal")

    if False :
        plotfunc.AddHistogram(bg_canvas,experimentalPlot,'lE3')

    # Experiment with food uncertainties only
    containers_food = Fitting.MakeFoodDeepCopies(containers)
    Fitting.PrepareBGMeasurementsForFit(containers,bwzProfile)
    fit_success = Fitting.MinimizeAllChi2(containers_food,bwzProfile)
    food_fit_plot = PredictionPlots(containers_food,bwzProfile,week,day,nHours=nHours)
    food_fit_plot.SetTitle("Fit (food hypothesis)")
    food_fit_plot.SetLineWidth(3)

    if fit_success :
        plotfunc.AddHistogram(bg_canvas,food_fit_plot,'lE3')

    # Continue the experiment! (Re-use the existing modified containers)
    fit2_success = Fitting.BalanceFattyEvents(containers_food,bwzProfile)
    food_fit_plot_v2 = PredictionPlots(containers_food,bwzProfile,week,day,nHours=nHours)
    food_fit_plot_v2.SetTitle("Fit (balance food and fatty event)")
    food_fit_plot_v2.SetLineWidth(3)
    food_fit_plot_v2.SetLineColor(ROOT.kBlue)
    food_fit_delta_v2 = GetDeltaBGversusTimePlot('FoodOrLiver_fit_v2',containers_food,positive_bg_items,bwzProfile,week,day,doStack=False,nHours=nHours)

    if fit2_success :
        plotfunc.AddHistogram(bg_canvas,food_fit_plot_v2,'lE3')

    plotfunc.MakeLegend(bg_canvas,0.18,0.68,0.38,0.88,option='l',textsize=14)

    # Make suggestions:
    for c in containers_food :
        if c.iov_0 < MyTime.WeekDayHourToUniversal(week,day,0) :
            continue
        if hasattr(c,'PrintSuggestion') :
            c.PrintSuggestion(bwzProfile)

    #
    # Make the food and insulin blobs
    #
    food_plot = GetDeltaBGversusTimePlot('FoodOrLiver',containers,positive_bg_items,bwzProfile,week,day,doStack=True,nHours=nHours)
    delta_canvas.cd()
    food_plot.Draw('lsame')
    plotfunc.tobject_collector.append(food_plot)

    insulin_plot = GetDeltaBGversusTimePlot('BolusOrBasal',containers,negative_bg_items,bwzProfile,week,day,doStack=True,nHours=nHours)
    delta_canvas.cd()
    insulin_plot.Draw('lsame')
    plotfunc.tobject_collector.append(insulin_plot)

    both_plot = GetDeltaBGversusTimePlot('FoodOrBolus',containers,positive_bg_items + negative_bg_items,bwzProfile,week,day,nHours=nHours)
    both_plot.SetLineWidth(2)
    plotfunc.AddHistogram(delta_canvas,both_plot,'lhist')

    basal_schedule_plot = GetDeltaBGversusTimePlot('ScheduledBasal',[basal_schedule],['BasalInsulin'],bwzProfile,week,day,nHours=nHours)
    basal_schedule_plot.SetLineStyle(7)
    basal_schedule_plot.SetLineWidth(2)
    plotfunc.AddHistogram(delta_canvas,basal_schedule_plot,'lhist')

    delta_canvas.cd()
    food_fit_delta_v2.Draw('lsame')
    plotfunc.tobject_collector.append(food_fit_delta_v2)

    do_propaganda = True

    if do_propaganda :
        leg = ROOT.TLegend(0.00,0.40,0.15,0.58)
        leg.SetFillStyle(0)
        leg.SetTextSize(12)
        for it in positive_bg_items :
            label = it.replace('Liver','').replace('Insulin','').replace('Effect','')
            label = label.replace('SquareWaveBolus','Square wave')
            entry = leg.AddEntry(None,label,'f')
            entry.SetFillColor(PlotManagement.GetColor(it))
            entry.SetFillStyle(3000)
            entry.SetLineColor(PlotManagement.GetColor(it))
        leg.Draw()
        plotfunc.tobject_collector.append(leg)

        leg2 = ROOT.TLegend(0.00,0.04,0.15,0.28)
        leg2.SetFillStyle(0)
        leg2.SetTextSize(12)
        for it in negative_bg_items :
            label = it.replace('Liver','').replace('Insulin','').replace('Effect','')
            label = label.replace('SquareWaveBolus','Square wave')
            entry = leg2.AddEntry(None,label,'f')
            entry.SetFillColor(PlotManagement.GetColor(it))
            entry.SetFillStyle(3001)
            entry.SetLineColor(PlotManagement.GetColor(it))
        leg2.Draw()
        plotfunc.tobject_collector.append(leg2)

    a = ROOT.TLine()
    a.DrawLine(-0.5,0,nHours + 0.5,0)
    plotfunc.tobject_collector.append(a)
    delta_canvas.RedrawAxis()

    #
    # Make the residual plots
    #
    if residual_canvas :

        # Residual plot for sensor data
        if sensor_data.GetN() > 1 :
            residual_plot = ComparePredictionToReality(prediction_plot,sensor_data)
            residual_plot.SetMarkerSize(0.5)
            plotfunc.AddHistogram(residual_canvas,residual_plot,'p')

        # Residual plot for BG data
        residual_plot_2 = ComparePredictionToReality(prediction_plot,bg_data)
        residual_plot_2.SetMarkerSize(0.8)
        residual_plot_2.SetMarkerColor(ROOT.kRed+1)
        plotfunc.AddHistogram(residual_canvas,residual_plot_2,'p')

    # Draw the container details
    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0)
    DrawEventDetails(containers,start_of_plot_day,delta_canvas,bwzProfile)

    #
    # Draw the date.
    #
    plotfunc.DrawText(prediction_canvas.GetPrimitive('pad_top'),
                      MyTime.StringFromTime(MyTime.DayWeekToUniversal(week,day),dayonly=True),
                      0.79,0.73,0.91,0.84,
                      totalentries=1
                      )

    def AddSettingsHistogram(can,hist,color) :
        hist.SetMarkerColor(color)
        hist.SetMarkerSize(0.2)
        plotfunc.AddHistogram(settings_canvas,hist,'p')
        hist.SetMarkerSize(6)
        plotfunc.AddHistogram(settings_canvas,hist,'text45')

    if settings_canvas :
        # Draw settings - insulin sensitivity
        # For now, just find the latest histogram
        hist_sensi = sensi_histograms.latestHistogram().Clone('hist_sensi')
        AddSettingsHistogram(settings_canvas,hist_sensi,ROOT.kGreen+1)

        # Draw settings - food sensitivity
        hist_ric = ric_histograms.latestHistogram().Clone('hist_ric')
        AddSettingsHistogram(settings_canvas,hist_ric,ROOT.kRed+1)

        # Draw settings - basal
        hist_basal = basal_histograms.latestHistogram().Clone('hist_basal')
        AddSettingsHistogram(settings_canvas,hist_basal,ROOT.kBlue+1)

    for can in [settings_canvas,delta_canvas,residual_canvas,prediction_canvas] :
       if not can :
           continue
       can.Modified()
       can.Update()

    print '\nBWZ profile:'
    bwzProfile.Print()

    print '\nNew profile:'
    experimentalProfile.Print()

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

    for j in range(i-1,0,-1) :
        tree.GetEntry(j)
        if tree.BGReading > 0 :

            UT_previous = tree.UniversalTime
            bg_read = tree.BGReading

            # Reset the tree to the entry we were at:
            tree.GetEntry(i)

            # break by returning
            return UT_previous,bg_read

    print 'Error - cannot find previous BG! Exiting.'
    import sys; sys.exit()
    return 0,0

#------------------------------------------------------------------
def FindSuspendEnd(tree,i) :
    found_end = False

    for j in range(i,i+30) :
        tree.GetEntry(j)
        if tree.SuspendEnd > 0 :
            UT_next = tree.UniversalTime
            found_end = True
            break

    if not found_end :
        print 'Error - could not find end of the Suspend!'
        import sys; sys.exit();

    # Reset the tree to the entry we were at:
    tree.GetEntry(i)

    return UT_next

#------------------------------------------------------------------
def FindTempBasalEnd(tree,i) :
    found_end = False

    for j in range(i,i+30) :
        tree.GetEntry(j)
        if tree.TempBasalEnd > 0 :
            UT_next = tree.UniversalTime
            found_end = True
            break

    if not found_end :
        print 'Error - could not find end of the Temp basal!'
        UT_next = MyTime.timerightnow + 3*MyTime.OneHour
        #import sys; sys.exit();

    # Reset the tree to the entry we were at:
    tree.GetEntry(i)

    return UT_next

#------------------------------------------------------------------
def GetDayContainers(tree,week,day,nHours=24) :

    print 'Called LoadDayEstimate'
    print '%%%%%%%%%%%%%%%%%%%'
    print ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day]
    print MyTime.StringFromTime(MyTime.WeekDayHourToUniversal(week,day,0))
    print '%%%%%%%%%%%%%%%%%%%'

    # The start of what we will plot (we will find the first BG before then):
    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0) # from 4am

    # The start-time of relevant events is 6 hours before the first BG measurement (found below).
    # We consider earlier events because they can bleed into the next day.
    start_time_relevantEvents = 0

    # When to start printing out the bolus info to command-line
    start_printouts = MyTime.WeekDayHourToUniversal(week,day,0) - 6*MyTime.OneHour

    # The end-time - 4am the next day (or otherwise specified)
    end_time = MyTime.WeekDayHourToUniversal(week,day + int(nHours/24),int(nHours)%24)

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
            UT_next = tree.UniversalTime
            UT_previous,bg_read = FindTimeAndBGOfPreviousBG(tree,i)

            # Make the "First BG" container entry:
            c = BGMeasurement(UT_previous,UT_next,bg_read)
            c.firstBG = True
            containers.append(c)

            # Anything 12h before first measurement is a relevant event
            start_time_relevantEvents = UT_previous - 12.*MyTime.OneHour

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
            iov_1 = min(FindTimeOfNextBG(tree,i),end_time)
            c = BGMeasurement(tree.UniversalTime,iov_1,tree.BGReading)
            containers.append(c)


        # Insulin
        if tree.BolusVolumeDelivered > 0 :

            ut = tree.UniversalTime
            c = InsulinBolus(ut, tree.BolusVolumeDelivered)

            # Matching BWZEstimate from delivered insulin
            IsBWZEstimate = False

            # Try to find (within 5 seconds) the bolus wizard estimate
            for j in range(i-1,i-10,-1) + range(i+1,i+10) :
                tree.GetEntry(j)
                if tree.BWZEstimate > 0 and (abs(tree.UniversalTime - c.iov_0) < 5*MyTime.OneSecond) :
                    c.BWZEstimate           = tree.BWZEstimate
                    c.BWZInsulinSensitivity = tree.BWZInsulinSensitivity
                    c.BWZCorrectionEstimate = tree.BWZCorrectionEstimate
                    c.BWZFoodEstimate       = tree.BWZFoodEstimate
                    c.BWZActiveInsulin      = tree.BWZActiveInsulin
                    c.BWZBGInput            = tree.BWZBGInput
                    c.BWZCarbRatio          = tree.BWZCarbRatio
                    IsBWZEstimate = True
                    break

            # Reset tree entry
            tree.GetEntry(i)

            if not IsBWZEstimate :
                print 'Warning! Could not find BWZ estimate!',MyTime.StringFromTime(c.iov_0)

            if IsBWZEstimate and (c.insulin != c.BWZEstimate) :
                c.BWZMatchedDelivered = False

            if c.iov_0 > start_printouts :
                c.PrintBolus()

            containers.append(c)

        #
        # Square wave bolus (not dual+square)
        #
        if tree.BolusVolumeDeliveredDelayed > 0 :

            ut = tree.UniversalTime
            c = SquareWaveBolus(ut,tree.ProgrammedBolusDuration,tree.BolusVolumeDeliveredDelayed)
            containers.append(c)

            if c.iov_0 > start_printouts :
                c.Print()

        #
        # Food
        #
        if tree.BWZCarbInput > 0 :

            ut = tree.UniversalTime

            c = Food(ut, ut + 6.*MyTime.OneHour, tree.BWZCarbInput)
            c.BWZInsulinSensitivity = tree.BWZInsulinSensitivity
            c.BWZCarbRatio = tree.BWZCarbRatio
            c.UserInputCarbSensitivity = 2.

            # starting on March 25, 2015:
            if tree.UniversalTime > MyTime.TimeFromString('03/25/15 10:00:00') :
                add_time = (tree.BWZCarbInput % 5)
                #print 'Grading based on %5.',
                #print 'Food was %d. New decay time: %2.1f.'%(tree.BWZCarbInput,2. + add_time)
                c.UserInputCarbSensitivity = 2. + add_time

            print 'Food, %s : %2.0fg\n'%(MyTime.StringFromTime(c.iov_0),c.food)
            containers.append(c)

        #
        # Suspend
        #
        if tree.SuspendStart :
            ut = tree.UniversalTime
            c = Suspend(ut,FindSuspendEnd(tree,i))
            print 'Suspend, %s - %s\n'%(MyTime.StringFromTime(c.iov_0),MyTime.StringFromTime(c.iov_1))
            containers.append(c)

        #
        # Temp basal
        #
        if tree.TempBasalAmount > 0 :

            ut = tree.UniversalTime

            # Temp basal amount is assumed to be percent
            ut_end = FindTempBasalEnd(tree,i)
            print 'Temp Basal, %s - %s : %2.2f%%\n'%(MyTime.StringFromTime(ut),MyTime.StringFromTime(ut_end),tree.TempBasalAmount*100)
            c = TempBasal(ut,ut_end,tree.TempBasalAmount)
            containers.append(c)

        # Annotations
        if len(tree.annotation.replace('\x00','').strip()) :
            ut = tree.UniversalTime
            c = Annotation(ut,ut,tree.annotation)
            print 'Annotation, %s: \"%s\"'%(MyTime.StringFromTime(c.iov_0),c.annotation)
            containers.append(c)

        # exercise
        if tree.ExerciseDuration > 0 :
            ut = tree.UniversalTime
            c = ExerciseEffect(ut,ut + tree.ExerciseDuration*MyTime.OneHour,tree.ExerciseIntensity)
            print 'Exercise, %s: Duration %.1fh Intensity %.1f'%(MyTime.StringFromTime(c.iov_0),tree.ExerciseDuration,c.factor)
            containers.append(c)


    # Clean containers using the annotations
    containers_cleaned = []
    for c in containers :
        keep = True

        if c.IsAnnotation() :
            continue

        for annot in containers :
            if not annot.IsAnnotation() :
                continue

            #Look for exact match on iov_0
            if annot.iov_0 != c.iov_0 :
                continue

            if annot.annotation == 'cancelFood' :
                print 'Removing food at %s\n'%(MyTime.StringFromTime(c.iov_0))
                keep = False
                break

        if keep :
            containers_cleaned.append(c)

    def MyFn(c) :
        return c.iov_0

    containers_cleaned_sorted = sorted(containers_cleaned,key=MyFn)

    return containers_cleaned_sorted

#------------------------------------------------------------------
def ComparePredictionToReality(prediction,reality) :
    from array import array
    import math

    h = ROOT.TGraph()
    h.SetName('Compare_prediction_to_reality')

    max_time_delta = 1./6. # 10 minutes. Compare to "hours_per_step" in the PredictionPlots.

    # Try to assign a comparison for every reality point
    for i in range(reality.GetN()) :
        min_x_diff = 9999999
        best_comparison = 9999999
        reality_x = reality.GetX()[i]

        # Loop through prediction points, find the closest one
        for j in range(prediction.GetN()) :

            x_diff = reality_x - prediction.GetX()[j]

            # Often we reset our future prediction to this BG, so that would be unfair.
            if x_diff < 0 :
                continue

            # if it is farther away from 10 minutes, then dont bother
            if math.fabs(x_diff) > max_time_delta :
                continue

            # If we find a better one, replace it with that one
            if x_diff < min_x_diff :
                min_x_diff = x_diff
                best_comparison = reality.GetY()[i] - prediction.GetY()[j]

        if min_x_diff < 9999999 :
            h.SetPoint(h.GetN(),reality_x,best_comparison)

    return h

#------------------------------------------------------------------
def GetDeltaBGversusTimePlot(name,containers,match_to,settings,week,day,doStack=False,nHours=24) :
    #
    # Plot the deltaBG per hour. Because it is per hour, and plotted versus hour, the integral
    # is the total dose.
    # match_to needs to be ['Food','InsulinBolus','LiverBasalGlucose'] or some combination
    #
    import math

    start_of_plot_day = MyTime.WeekDayHourToUniversal(week,day,0) # from 4am
    hours_per_step = 0.1
    hist_args = (int(nHours/float(hours_per_step)),0,int(nHours))
    tag = '%d_%d_%s'%(week,day,name)

    c_hists = []
    toggleLightDark = True

    h_basalglucose = None
    h_basalinsulin = None
    h_tempglucose = []

    for ci,c in enumerate(containers) :

        classname = c.__class__.__name__

        # check c.IsBolus(), c.IsFood() or c.IsFoodOrBolus()
        if not classname in match_to :
            continue

        hist = ROOT.TH1F('%s_%d'%(tag,ci),'asdf',*hist_args)

        color = ROOT.kBlack
        if doStack :
            color = PlotManagement.GetColor(classname)

        hist.SetFillColorAlpha(color,0.4 + 0.2*(toggleLightDark)) # alternate dark and light
        toggleLightDark = not toggleLightDark
        hist.SetLineColorAlpha(color+1,1)
        hist.SetLineWidth(1)

        for i in range(int(nHours/float(hours_per_step))+1) :

            time_ut = start_of_plot_day + i*hours_per_step*float(MyTime.OneHour)
            hist.SetBinContent(i+1,c.getBGEffectDerivPerHour(time_ut,settings))

        if classname == 'BasalInsulin' :
            h_basalinsulin = hist
        elif classname == 'LiverBasalGlucose' :
            h_basalglucose = hist
        elif classname == 'LiverFattyGlucose' :
            h_tempglucose.append(hist)
        else :
            c_hists.append(hist)

    if doStack :
        h_ret = ROOT.THStack('stack_%s'%(tag),'stack')
    else :
        h_ret = ROOT.TH1F('%s'%(tag),'asdf',*hist_args)

    # Add the histograms in a particular order:
    if h_basalglucose :
        h_ret.Add(h_basalglucose)
    if h_basalinsulin :
        h_ret.Add(h_basalinsulin)
    for h in reversed(h_tempglucose) :
        h_ret.Add(h)
    for h in reversed(c_hists) :
        h_ret.Add(h)

    return h_ret

#------------------------------------------------------------------
def PredictionPlots(containers,settings,week,day,nHours=24,doReset=True) :
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
    hours_per_step = 0.1

    prediction_graph = ROOT.TGraph()
    prediction_graph.SetTitle('prediction')

    bg_estimates = []

#     for c in containers :
#         c.Print()

    # When we hit a BG reading, then we want to consider (once) resetting the prediction.
    already_considered_for_bgReset = []

    for i in range(int(nHours/float(hours_per_step))) :

        the_time = start_of_plot_day + i*hours_per_step*float(MyTime.OneHour) # universal
        time_on_plot = hours_per_step*i

        # We start the estimate with the estimate from the previous point.
        # We then calculate the differential effect of each object.
        # The effects are assumed to be additive.
        # If this is the first point, then we start with the last BG estimate from the previous day.
        if len(bg_estimates) == 0 :
            first_bg = findFirstBG(containers)
            bg_estimates.append(first_bg.const_BG)

            # We have effectively already considered this BG for reset.
            already_considered_for_bgReset.append(first_bg.iov_0)

        else :
            bg_estimates.append( bg_estimates[-1] )

        # We'll keep track of whether large boluses are in progress in this time-step
        max_bgEffectRemaining = 0

        for c in containers :

            if the_time < c.iov_0 :
                continue

            # Special treatment for the first bin of the day:
            if (i==0) and c.AffectsBG() :

                # Find the first BG
                first_bg_time = findFirstBG(containers).iov_0

                # Add the integral from the first BG time up to this time
                bg_estimates[-1] += c.getIntegral(first_bg_time,the_time,settings)

                continue

            # If the object time has expired, skip it.
            if the_time > c.iov_1 :
                continue

            # For the typical bin in the day-plot:
            if c.AffectsBG() :
                impactInTimeInterval = c.getBGEffectDerivPerHourTimesInterval(the_time,hours_per_step,settings)
                bg_estimates[-1] += impactInTimeInterval
                max_bgEffectRemaining = max(max_bgEffectRemaining,math.fabs(c.BGEffectRemaining(the_time,settings)))

            # If there was a new reading, we reset the prediction (with the caveats below)
            if c.IsMeasurement() and not (c.iov_0 in already_considered_for_bgReset) :

                # We should only consider resetting one time!
                already_considered_for_bgReset.append(c.iov_0)

                if not doReset :
                    continue

                # If nothing is in progress that would cause 30 points drop/increase,
                # reset the prediction.
                if max_bgEffectRemaining < 30 :
                    bg_estimates[-1] = c.const_BG

        # end loop over containers

        # add a new point to the graph
        prediction_graph.SetPoint(prediction_graph.GetN(),time_on_plot,bg_estimates[-1])

    return prediction_graph
