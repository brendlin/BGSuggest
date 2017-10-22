import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc
from PyBGSuggestHelpers import TimeClass,BGFunction,PredictionPlots,GetIntegratedAverage,GetHistWithTimeAxis
import ROOT

def SampleEarlyBolus() :

    t = TimeClass()

    tf1s = []
    ntest = 3
    for x in range(ntest) :
        #
        # Overrides
        #
        start_of_plot_day = t.WeekDayHourToUniversal(0,x,0)
        containers = []

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
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,0)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,1)
        containers[-1].type     = 'First BG'
        containers[-1].const_BG = 115.

        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,1)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,23)
        containers[-1].type     = 'BGReading'
        containers[-1].const_BG = 115.

        #
        # breakfast
        #
        meal = 0
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,5-OFFSET[x]) # 9am
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,11)
        containers[-1].type     = 'Insulin'
        containers[-1].S        = 65.
        containers[-1].Ta       = 4.
        containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
        #
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,5) # 9am
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,11)
        containers[-1].type     = 'Food'
        containers[-1].S        = 65.
        containers[-1].Ta       = 2.
        containers[-1].C        = NFOOD[meal]*FACTOR[x]
        containers[-1].RIC      = RATIO

        #
        # lunch
        #
        meal = 1
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,8-OFFSET[x])
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,14)
        containers[-1].type     = 'Insulin'
        containers[-1].S        = 65.
        containers[-1].Ta       = 4.
        containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
        #
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,8)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,14)
        containers[-1].type     = 'Food'
        containers[-1].S        = 65.
        containers[-1].Ta       = 2.
        containers[-1].C        = NFOOD[meal]*FACTOR[x]
        containers[-1].RIC      = RATIO

        #
        # snack
        #
        meal = 2
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,12-OFFSET[x])
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,18)
        containers[-1].type     = 'Insulin'
        containers[-1].S        = 65.
        containers[-1].Ta       = 4.
        containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
        #
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,12)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,18)
        containers[-1].type     = 'Food'
        containers[-1].S        = 65.
        containers[-1].Ta       = 2.
        containers[-1].C        = NFOOD[meal]*FACTOR[x]
        containers[-1].RIC      = RATIO

        #
        # dinner
        #
        meal = 3
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,16-OFFSET[x])
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,22)
        containers[-1].type     = 'Insulin'
        containers[-1].S        = 65.
        containers[-1].Ta       = 4.
        containers[-1].I0       = NFOOD[meal]*FACTOR[x]/float(RATIO)
        #
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,16)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,22)
        containers[-1].type     = 'Food'
        containers[-1].S        = 65.
        containers[-1].Ta       = 2.
        containers[-1].C        = NFOOD[meal]*FACTOR[x]
        containers[-1].RIC      = RATIO

        #
        # "final reading"
        #
        containers.append(BGFunction())
        containers[-1].iov_0    = t.WeekDayHourToUniversal(0,x,23)
        containers[-1].iov_1    = t.WeekDayHourToUniversal(0,x,25)
        containers[-1].type     = 'BGReading'
        containers[-1].const_BG = 115.

        #print x
        tf1s.append(PredictionPlots(containers,0,x))
        key = NAMES[x]+' (IBG=%2.2f)'%GetIntegratedAverage(tf1s[-1])
        tf1s[-1].SetNameTitle(key,key)
        #daytitle = daytitles.get(x,'Noneday')
        #key = daytitle+' sample'
        #tf1s[-1].SetNameTitle(key,key)

    tf1sNOASYM = []
    for i in range(len(tf1s)) :
        tf1sNOASYM.append(ROOT.TGraph(tf1s[i].GetN(),tf1s[i].GetX(),tf1s[i].GetY()))
        key = tf1s[i].GetName()
        tf1sNOASYM[-1].SetNameTitle(key,key)

#         sample_hist = SmartPlot(0,'','Reduced Carbohydrate Example',[hist]+tf1sNOASYM,ranges=[[0,24],[40,450]],drawopt='')
#         for i in range(ntest) :
#             sample_hist.plots[i+1].SetDrawOption('p')
#             sample_hist.plots[i+1].SetMarkerColor(color[i])
#             sample_hist.plots[i+1].SetLineColor(color[i])
#         sample_hist.CreateLegend(.5,.65,.95,.88)
#         sample_hist.SetLegend(skip=[0])
#         sample_hist.can.cd()
#         sample_hist.leg.Draw()
#         sample_hist.SetAxisLabels('Time','BG')

    sample_canvas = ROOT.TCanvas('Reduced_Carbohydrate_Example','Reduced Carbohydrate Example',500,500)
    plotfunc.AddHistogram(sample_canvas,GetHistWithTimeAxis())
    for i in tf1sNOASYM :
        plotfunc.AddHistogram(sample_canvas,i,'p')
    taxisfunc.SetYaxisRanges(sample_canvas,40,450)
    plotfunc.SetColors(sample_canvas)
    plotfunc.MakeLegend(sample_canvas)
    plotfunc.SetAxisLabels(sample_canvas,'Time','BG')
# SmartPlot(0,'','Reduced Carbohydrate Example',[hist]+tf1sNOASYM,ranges=[[0,24],[40,450]],drawopt='')
#         for i in range(ntest) :
#             sample_hist.plots[i+1].SetDrawOption('p')
#             sample_hist.plots[i+1].SetMarkerColor(color[i])
#             sample_hist.plots[i+1].SetLineColor(color[i])
#         sample_hist.CreateLegend(.5,.65,.95,.88)
#         sample_hist.SetLegend(skip=[0])
#         sample_hist.can.cd()
#         sample_hist.leg.Draw()
#         sample_hist.SetAxisLabels('Time','BG')

    return sample_canvas
