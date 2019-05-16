from PyBGSuggestHelpers import a1cToBS,RootMeanSquare,TimeClass
import PlotFunctions as plotfunc
import ROOT
from array import array

#-------------------------------------------------------------------------
def GetAverageBGs(hist,tree,last_week,n_weeks=1) :

    all_vals = []

    for i in range(last_week+1) :

        all_vals.append([])

        req = 'BGReading > 0 && WeekOfYear <= %d && WeekOfYear > %d'%(i,i-n_weeks)
        n = tree.Draw('BGReading>>hist%d(100,0,500)'%(i+1),req,'goff')
        #print req,n

        if not n :
            continue

        Avg = 0
        for x in range(n) :
            Avg += tree.GetV1()[x]
            all_vals[-1].append(tree.GetV1()[x])

        Avg = Avg / float(n)

        if Avg == 0 :
            continue

        hist.SetBinContent(i+1,Avg)
        hist.SetBinError(i+1,RootMeanSquare(all_vals[-1]))

    return all_vals

#-------------------------------------------------------------------------
def GetAverageBGsCoarse(hist,all_vals,n_weeks) :
    # all_vals is the list of lists from GetAverageBGs (when 1 week is specified)
    # n_weeks is the number of weeks to average over

    for i in range(len(all_vals)) :
        min_index = max(0,i+1-n_weeks)
        to_consider = all_vals[min_index:i+1]

        # This is the x-value (bin center)
        xval = i+0.5

        # Figure out how many weeks are populated:
        week_populated = list(len(j) > 0 for j in to_consider)
        n_week_populated = week_populated.count(True)

        # Only compute the average if at least 1/2 of the weeks are populated
        # If data is stopped, then stop computing the average
        if (n_week_populated < (n_weeks/2)) or (len(to_consider[-1]) == 0) :

            # Collapse the error bar, if necessary
            if hist.GetN() and hist.GetX()[hist.GetN()-1] == xval-1 and issubclass(type(hist),type(ROOT.TGraphErrors())) :
                new_point = hist.GetN()
                hist.SetPoint(new_point,xval-0.5,hist.GetY()[hist.GetN()-1])
                hist.SetPointError(new_point,0,0)

            continue

        Avg = 0
        n = 0
        vals = []
        for week in to_consider :
            for val in week :
                vals.append(val)
                Avg += val
                n += 1

        Avg = Avg / float(n)

        # If previous point is missing, set the error to 0 :
        if (hist.GetN() == 0 or hist.GetX()[hist.GetN()-1] < xval-1) and issubclass(type(hist),type(ROOT.TGraphErrors())) :
            new_point = hist.GetN()
            hist.SetPoint(new_point,xval-0.5,Avg)
            hist.SetPointError(new_point,0,0)

        # Set the point
        new_point = hist.GetN()
        hist.SetPoint(new_point,xval,Avg)
        if issubclass(type(hist),type(ROOT.TGraphErrors())) :
            hist.SetPointError(new_point,0,RootMeanSquare(vals))

    return

#-------------------------------------------------------------------------
def YearInReview(tree,nyears=7) :

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
    perweek_vals = GetAverageBGs(yir,tree,last_week)

    yir_smooth = ROOT.TGraph()
    yir_smooth.SetTitle('4-week average')
    GetAverageBGsCoarse(yir_smooth,perweek_vals,4)

    yir_17w = ROOT.TGraphErrors()
    yir_17w.SetTitle('17-week average')
    GetAverageBGsCoarse(yir_17w,perweek_vals,17)
    yir_17w_noerr = ROOT.TGraph(yir_17w.GetN(),yir_17w.GetX(),yir_17w.GetY())

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
    for line in open('data/a1c.csv').readlines() :
        line = line.replace('\n','')
        date = line.split(',')[0].lstrip(' ').rstrip(' ')
        a1c  = line.split(',')[1].lstrip(' ').rstrip(' ')
        a1x.append(t.GetWeekOfYear(t.TimeFromString('%s 04:00:00'%(date))))
        a1y.append(a1cToBS(float(a1c))[0])

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
    a1cs.SetLineWidth(1)
    a1cs.SetLineColor(a1c_color)
    a1cs.SetMarkerStyle(22)

    labels = {0:'Jan-Mar',
              1:'Apr-Jun',
              2:'Jul-Sep',
              3:'Oct-Dec'
              }

    dummy = ROOT.TH1F('dummy','remove',nyears*4,0,365*nyears/7)
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
    year_in_review = ROOT.TCanvas(yir_name,yir_title,1270,500)
    year_in_review.SetLeftMargin(0.16/2.)
    year_in_review.SetRightMargin(0.16/2.)
    year_in_review.SetBottomMargin(0.12)

    def Prepare(hist,color) :
        hist.SetLineColor(color)
        hist.SetMarkerColor(color)
        if hist.GetMarkerColor() == 0 :
            hist.SetMarkerColor(1)
        hist.SetFillColorAlpha(color,0.3)
        hist.SetLineWidth(2)
        return

    Prepare(yir_17w,ROOT.kAzure-2)
    Prepare(yir_17w_noerr,ROOT.kAzure-2)
    Prepare(yir,ROOT.kBlack)
    Prepare(yir_smooth,ROOT.kRed+1)

    #yir_17w.SetFillStyle(3001)
    yir_smooth.SetFillStyle(0)

    plotfunc.AddHistogram(year_in_review,dummy)
    yir_17w.SetMarkerSize(0)
    yir_17w.SetTitle('17-week-average')
    plotfunc.AddHistogram(year_in_review,yir_17w,'lE3')
    yir.SetMarkerSize(0.7)
    plotfunc.AddHistogram(year_in_review,yir,'phist')
    plotfunc.AddHistogram(year_in_review,yir_smooth,'l')
    # Add yir on top once more.
    yir_17w.SetFillStyle(0)
    yir_17w.SetTitle('remove')
    plotfunc.AddHistogram(year_in_review,yir_17w_noerr,'l')
    plotfunc.AddHistogram(year_in_review,a1cs,'pl')
    plotfunc.AutoFixAxes(year_in_review)
    plotfunc.SetAxisLabels(year_in_review,'','#LT^{}BG#GT (mg/dL)')
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

    option = ['fl','l','l','pl','pl']
    plotfunc.MakeLegend(year_in_review,0.7,0.15,0.86,0.35,option=option)
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
    other_axis.SetTitleOffset(0.7)
    other_axis.SetTitle('HbA_{1}c (%)')
    global tobject_collector;
    plotfunc.tobject_collector.append(other_axis)
    other_axis.Draw()

    year_in_review.SetGrid()
    year_in_review.Modified()
    year_in_review.Update()

    return year_in_review
