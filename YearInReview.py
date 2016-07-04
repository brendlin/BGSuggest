from PyBGSuggestHelpers import a1cToBS,RootMeanSquare,TimeClass
import pennSoftLepton.PlotFunctions as plotfunc
import ROOT
from array import array

def GetAverageBGs(hist,tree,last_week,n_weeks) :
    for i in range(last_week+1) :
        req = 'BGReading > 00 && WeekOfYear <= %d && WeekOfYear > %d-%d'%(i+1,i+1,n_weeks)
        #req = 'BGReading > 00 && WeekOfYear == %d'%(i)
        n = tree.Draw('BGReading>>hist%d(100,0,500)'%(i+1),req,'goff')
        if not n : continue
        Avg = 0
        vals = []
        for x in range(n) :
            Avg += tree.GetV1()[x]
            vals.append(tree.GetV1()[x])
        Avg = Avg / float(n)

        if Avg == 0 : continue
        hist.SetBinContent(i+1,Avg)
        hist.SetBinError(i+1,RootMeanSquare(vals))

    return

#-------------------------------------------------------------------------
def YearInReview(tree,nyears=4) :

    #
    # Requred setup
    #
    t = TimeClass()

    last_week = 0
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        last_week = max(last_week,tree.WeekOfYear)

    nweeks = 365*nyears / 7
    print 'nweeks:',nweeks

    #
    # End required setup
    #

    yir = ROOT.TH1F('AverageBG','1-week average',last_week,0,last_week)
    GetAverageBGs(yir,tree,last_week,1)

    yir_smooth = ROOT.TH1F('4-week average','4-week average',last_week,0,last_week)
    GetAverageBGs(yir_smooth,tree,last_week,4)

    yir_17w = ROOT.TH1F('17-week average','17-week average',last_week,0,last_week)
    GetAverageBGs(yir_17w,tree,last_week,17)

    yir_food = ROOT.TH1F('Food Intake','Food Intake',nweeks,0,nweeks)
    for i in range(last_week+1) :
        req = 'BWZCarbInput > 00 && WeekOfYear == %d'%(i)
        n = tree.Draw('BWZCarbInput>>hist%d(100,-500,500)'%(i),req,'goff')
        if not n : continue
        Tot = 0
        for x in range(n) :
            Tot += tree.GetV1()[x]
        yir_food.SetBinContent(i+1,Tot/10.)

    a1x = []
    a1y = []
    # May 30, 2012 : 7.7 (last result from SHS)
    # january
    a1x.append(t.GetWeekOfYear(t.TimeFromString('01/12/13 04:00:00')))
    a1y.append(a1cToBS(7.9)[0])
    # april
    a1x.append(t.GetWeekOfYear(t.TimeFromString('04/13/13 04:00:00')))
    a1y.append(a1cToBS(8.0)[0])
    # august
    a1x.append(t.GetWeekOfYear(t.TimeFromString('08/19/13 04:00:00')))
    a1y.append(a1cToBS(7.7)[0])
    # december
    a1x.append(t.GetWeekOfYear(t.TimeFromString('12/19/13 04:00:00')))
    a1y.append(a1cToBS(7.6)[0])
    # april
    a1x.append(t.GetWeekOfYear(t.TimeFromString('04/08/14 04:00:00')))
    a1y.append(a1cToBS(7.3)[0])
    # december 2014
    a1x.append(t.GetWeekOfYear(t.TimeFromString('12/16/14 04:00:00')))
    a1y.append(a1cToBS(7.4)[0])
    # september 2015
    a1x.append(t.GetWeekOfYear(t.TimeFromString('09/02/15 04:00:00')))
    a1y.append(a1cToBS(7.6)[0])
    #
    x_a1 = array('d',a1x)
    y_a1 = array('d',a1y)
    a1cs = ROOT.TGraph(len(x_a1),x_a1,y_a1)
    #a1csname = 'a1c, %s'%(a1cToBS(0.)[1])
    a1csname = 'HbA_{1}c'
    a1cs.SetNameTitle(a1csname,a1csname)
    a1c_color = ROOT.kOrange-3
    a1cs.SetMarkerColor(a1c_color)
    a1cs.SetMarkerStyle(20)
    a1cs.SetMarkerSize(1.5)
    a1cs.SetLineWidth(2)
    a1cs.SetLineColor(a1c_color)
    a1cs.SetMarkerStyle(22)

#     dayspermonth = {0 :['Jan', 31],
#                     1 :['Feb', 28],
#                     2 :['Mar', 31],
#                     3 :['Apr', 30],
#                     4 :['May', 31],
#                     5 :['Jun', 30],
#                     6 :['Jul', 31],
#                     7 :['Aug', 31],
#                     8 :['Sep', 30],
#                     9 :['Oct', 31],
#                     10:['Nov', 30],
#                     11:['Dec', 31]
#                     }

    labels = {0:'Jan-Mar',
              1:'Apr-Jun',
              2:'Jul-Sep',
              3:'Oct-Dec'
              }

    dummy = ROOT.TH1F('dummy','dummy',nyears*4,0,365*nyears/7)
    for mo3 in range(nyears * 4 - 1) :
        dummy.GetXaxis().SetBinLabel(mo3+1,'%s \'%d     '%(labels[mo3%4],13+mo3/4))

    #yir_type = 'ADA'
    formula_type = 'Kurt'
    if formula_type == 'ADA' :
        yir_type = 'ADA'
    else :
        yir_type = 'Ad Hoc'

    yir_name = 'yir'
    yir_title = 'Year In Review (%s)'%(yir_type)
    year_in_review = ROOT.TCanvas(yir_name,yir_title,1000,500)
    year_in_review.SetLeftMargin(0.16/2.)
    year_in_review.SetRightMargin(0.16/2.)
    year_in_review.SetBottomMargin(0.12)
    
    yir_17w.SetFillStyle(1001)

    def Prepare(hist,color) :
        hist.SetLineColor(color)
        hist.SetMarkerColor(color)
        if hist.GetMarkerColor() == 0 :
            hist.SetMarkerColor(1)
        hist.SetFillColor(color)
        hist.SetLineWidth(2)
        return

    Prepare(yir_17w,ROOT.kAzure-2)
    Prepare(yir,ROOT.kBlack)
    Prepare(yir_smooth,ROOT.kRed+1)

#     yir_17w.SetFillColor(ROOT.kBlue-10)
#     yir_smooth.SetFillColor(ROOT.kRed-10)
    yir_17w.SetFillStyle(3154)
    yir_smooth.SetFillStyle(3154)

    plotfunc.AddHistogram(year_in_review,dummy)
    yir_17w.SetTitle('skipme')
    plotfunc.AddHistogram(year_in_review,yir_17w,'E3')
    yir_17w.SetTitle('17-week average')
    plotfunc.AddHistogram(year_in_review,yir,'phist')
    plotfunc.AddHistogram(year_in_review,yir_smooth,'phist')
    plotfunc.AddHistogram(year_in_review,yir_17w,'phist')
    plotfunc.AddHistogram(year_in_review,a1cs,'pl')
    plotfunc.AutoFixAxes(year_in_review)
    plotfunc.SetAxisLabels(year_in_review,'','<BG> (mg/dL)')
    year_in_review.GetPrimitive('yir_dummy').GetYaxis().SetTitleOffset(0.8)
    year_in_review.GetPrimitive('yir_dummy').GetXaxis().SetLabelOffset(0.008)
    year_in_review.GetPrimitive('yir_dummy').GetXaxis().SetNdivisions(1,1,1,False)
    year_in_review.SetTicks(1,0)

    a = ROOT.TLine()
    a.SetLineWidth(2)
    low, med, high = a1cToBS(6.)[0],a1cToBS(7.)[0],a1cToBS(8.)[0]
    if formula_type == 'ADA' :
        low, med, high = 126,154,183
    if formula_type == 'sth' : # ????
        low, med, high = 136.3, 171.9, 207.5
    
    a.DrawLine(0,low,nweeks,low)
    a.DrawLine(0,med,nweeks,med)
    a.DrawLine(0,high,nweeks,high)
    a.DrawLine(last_week-16,low,last_week-16,high)

    option = ['p','p','fp','pl']
    plotfunc.MakeLegend(year_in_review,0.7,0.15,0.93,0.35,skip=['dummy'],option=option)
    year_in_review.GetPrimitive('legend').SetFillColor(0)
    year_in_review.GetPrimitive('legend').SetFillStyle(1001)

    a1cmin = (0-149.)/45. + 7
    a1cmax = (year_in_review.GetPrimitive('yir_dummy').GetMaximum()-149.)/45. + 7
    other_axis = ROOT.TGaxis(year_in_review.GetUxmax(),year_in_review.GetUymin(),
                             year_in_review.GetUxmax(),year_in_review.GetUymax(),a1cmin,a1cmax,510,"+L",0)
    other_axis.SetLabelFont(43)
    other_axis.SetLabelSize(22)
    other_axis.SetTitleFont(43)
    other_axis.SetTitleSize(22)
    print other_axis.SetTitleOffset(0.7)
    other_axis.SetTitle('HbA_{1}c (%)')
    global tobject_collector;
    plotfunc.tobject_collector.append(other_axis)
    other_axis.Draw()

    year_in_review.SetGrid()
    year_in_review.Modified()
    year_in_review.Update()

    return year_in_review
