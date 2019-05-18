import ROOT
from TimeClass import MyTime
#from PlotUtils import SmartPlot,color,markerstyles

def SuppliesSummary(tree,nyears=4) :

    NWEEKS=365*nyears / 7

    rewind_histo   = ROOT.TH1F('Rewind Frequency','Rewind Frequency',48,0,6)
    supplies_histo = ROOT.TH1F('Infusion Sets','Infusion Sets',NWEEKS,0,NWEEKS)
    strips_histo   = ROOT.TH1F('Test Strips /10','Test Strips /10',NWEEKS,0,NWEEKS)
    insulin_histo  = ROOT.TH1F('Insulin (mL, 10mL/vial)','Insulin (mL, 10mL/vial)',NWEEKS,0,NWEEKS)
    test_f_histo   = ROOT.TH1F('Test Frequency','Test Frequency',96,0,24)
    last_rewind     = 0
    last_bg         = 0
    rolling_rewinds = 0
    rolling_bgs     = 0
    first_week      = 0
    rolling_insulin = 0
    last_insulin    = 0
    week_in_question = first_week
    for i in range(tree.GetEntries()) :
        tree.GetEntry(i)
        if tree.WeekOfYear < first_week : continue
        if tree.WeekOfYear != week_in_question or (i == tree.GetEntries()-1) :
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
            if week_in_question == 63 : # purchased on March 5; accounting on March 19
                rolling_bgs      = 270./10.
            if week_in_question == 68 : # April 9
                rolling_bgs     += 500./10.
            if week_in_question == 80 : # July 11
                rolling_bgs     += 400./10.
                rolling_insulin += 60.
            if week_in_question == 82 : # July 25
                rolling_rewinds += 50.
            if week_in_question == 88 : # purchased Sept 11; accounting on Sept 16
                rolling_bgs      = 800./10. 
                rolling_insulin += 90. # not sure how much was actually picked up. Sept 11 email.
            supplies_histo.SetBinContent(week_in_question+1,rolling_rewinds)
            strips_histo.SetBinContent(week_in_question+1,rolling_bgs)
            insulin_histo.SetBinContent(week_in_question+1,rolling_insulin)
            week_in_question = tree.WeekOfYear
            #
            rolling_insulin = rolling_insulin - 2.5

        if tree.Rewind :
            rolling_rewinds -= 1
            if last_rewind :
                rewind_histo.Fill((tree.UniversalTime-last_rewind)/float(MyTime.OneDay))
            last_rewind = tree.UniversalTime
        if tree.BGReading > 0. :
            rolling_bgs -= 1/10.
            if last_bg :
                test_f_histo.Fill((tree.UniversalTime-last_bg)/float(MyTime.OneHour))
            last_bg = tree.UniversalTime

    #print week_in_question
    supplies_histo.SetBinContent(week_in_question+1,rolling_rewinds)
    strips_histo.SetBinContent(week_in_question+1,rolling_bgs)
    insulin_histo.SetBinContent(week_in_question+1,rolling_insulin)

#     rewind_plot = SmartPlot(0,'','Rewind Frequency',[rewind_histo],drawopt='hist')
#     rewind_plot.SetAxisLabels('Days between Rewinds','Entries')
#     test_f_histo.SetName('Test Frequency (avg=%2.2f/day)'%(24./float(test_f_histo.GetMean())))
#     test_f_plot = SmartPlot(0,'','Test Frequency',[test_f_histo],drawopt='hist')
#     test_f_plot.SetAxisLabels('Hours between tests','Entries')
#     supplies_plot = SmartPlot(0,'','Supplies Plot',[supplies_histo,strips_histo,insulin_histo],drawopt='hist')
#     supplies_plot.SetAxisLabels('Week Of Year','# of supplies')
    from ROOT import kRed,kAzure
    supplies_plot.plots[0].GetYaxis().SetRangeUser(0,120)
    supplies_plot.DrawHorizontal(30./3.,style=2)
    supplies_plot.DrawHorizontal(4.5*30./10.,style=2,color=kRed+1)
    supplies_plot.DrawTextNDC(.2,.135,'30 Days Left')
    supplies_plot.DrawTextNDC(.2,.20,'30 Days Left',color=kRed+1)
    supplies_plot.DrawTextNDC(.2,.235,'100 u/mL, 1000 u/vial',color=kAzure-2)

    return rewind_plot,supplies_plot,test_f_plot
