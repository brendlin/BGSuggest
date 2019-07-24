import ROOT
import PlotFunctions as plotfunc
import TAxisFunctions as taxisfunc

#------------------------------------------------------------------
def GetHistWithTimeAxis(nHours=24) :
    import ROOT
    if ROOT.gDirectory.Get('HistWithTimeAxis') :
        return ROOT.gDirectory.Get('HistWithTimeAxis')
    hist= ROOT.TH1F('HistWithTimeAxis','remove',nHours+1,-0.5,nHours + 0.5)
    hist.GetXaxis().SetBinLabel(1,'4am                   ')
    hist.GetXaxis().SetBinLabel(5,'8am')
    hist.GetXaxis().SetBinLabel(9,'12pm')
    hist.GetXaxis().SetBinLabel(13,'4pm')
    hist.GetXaxis().SetBinLabel(17,'8pm')
    hist.GetXaxis().SetBinLabel(21,'12am')
    hist.GetXaxis().SetBinLabel(29,'8am')
    return hist

#------------------------------------------------------------------
# Quick function to make target zones
def AddErrorBandHistogram(can,name,min,max,color,nHours=24) :
    average = (min + max) / float(2)
    difference = (min - max)
    band = ROOT.TH1F(name,'remove',1,0,nHours)
    band.SetBinContent(1,average)
    band.SetBinError(1,difference/float(2))
    band.SetFillColor(color)
    band.SetMarkerSize(0)
    plotfunc.AddHistogram(can,band,'E2')
    can.RedrawAxis()
    return

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
def FormatBGCanvas(prediction_canvas,nHours=24) :

    time_hist = GetHistWithTimeAxis(nHours)
    plotfunc.AddHistogram(prediction_canvas,time_hist,'')

    # Prediction canvas
    plotfunc.FormatCanvasAxes(prediction_canvas)
    taxisfunc.SetYaxisRanges(prediction_canvas,0.001,350)
    plotfunc.SetAxisLabels(prediction_canvas,'hr','BG (mg/dL)')

    # Green and yellow target zones
    AddErrorBandHistogram(prediction_canvas,'yellow',80,180,ROOT.kOrange,nHours)
    AddErrorBandHistogram(prediction_canvas,'green',100,150,ROOT.kGreen,nHours)

    return

#------------------------------------------------------------------
def FormatDeltaCanvas(delta_canvas,nHours=24) :

    time_hist = GetHistWithTimeAxis(nHours)
    plotfunc.AddHistogram(delta_canvas,time_hist,'')

    taxisfunc.SetYaxisRanges(delta_canvas,-299,299)
    taxisfunc.SetXaxisRanges(delta_canvas,-0.5,nHours + 0.5)
    taxisfunc.SetYaxisNdivisions(delta_canvas,5,5,0)
    xaxis = delta_canvas.GetPrimitive('pad_bot_HistWithTimeAxis').GetXaxis()
    xaxis.SetLabelOffset(0.02)
    plotfunc.SetAxisLabels(delta_canvas,'','#Delta^{}BG^{ }/^{ }hr')

    return

#------------------------------------------------------------------
def FormatThreePadCanvas(prediction_canvas,nHours=24) :

    bg_canvas = plotfunc.GetTopPad(prediction_canvas)
    delta_canvas = prediction_canvas.GetPrimitive('pad_mid')
    residual_canvas = plotfunc.GetBotPad(prediction_canvas)
    settings_canvas = prediction_canvas.GetPrimitive('pad_sub')

    # Add Time axis histogram to each sub-pad
    time_hist = GetHistWithTimeAxis(nHours)
    plotfunc.AddHistogram(prediction_canvas,time_hist,'')
    plotfunc.AddHistogram(residual_canvas,time_hist,'')
    plotfunc.AddHistogram(delta_canvas,time_hist,'')
    plotfunc.AddHistogram(settings_canvas,time_hist,'')

    # Prediction canvas
    plotfunc.FormatCanvasAxes(prediction_canvas)
    taxisfunc.SetYaxisRanges(prediction_canvas,0.001,350)
    plotfunc.SetAxisLabels(prediction_canvas,'hr','BG (mg/dL)')

    # Green and yellow target zones
    AddErrorBandHistogram(prediction_canvas,'yellow',80,180,ROOT.kOrange,nHours)
    AddErrorBandHistogram(prediction_canvas,'green',100,150,ROOT.kGreen,nHours)

    # Lumps
    taxisfunc.SetYaxisRanges(delta_canvas,-199,199)
    taxisfunc.SetXaxisRanges(delta_canvas,-0.5,nHours + 0.5)
    taxisfunc.SetYaxisNdivisions(delta_canvas,5,5,0)
    xaxis = delta_canvas.GetPrimitive('pad_mid_HistWithTimeAxis').GetXaxis()
    xaxis.SetLabelOffset(5)
    plotfunc.SetAxisLabels(delta_canvas,'','#Delta^{}BG^{ }/^{ }hr')

    # Residuals
    xaxis = residual_canvas.GetPrimitive('pad_bot_HistWithTimeAxis').GetXaxis()
    xaxis.SetLabelOffset(.04)
    xaxis.SetTitleOffset(2.8)
    plotfunc.SetAxisLabels(residual_canvas,'hr','data^{ }#minus^{ }pred')
    taxisfunc.SetYaxisRanges(residual_canvas,-199,199)
    taxisfunc.SetXaxisRanges(residual_canvas,-0.5,nHours + 0.5)

    # Settings
    plotfunc.FormatCanvasAxes(settings_canvas)
    plotfunc.SetAxisLabels(settings_canvas,'','Settings')
    xaxis = settings_canvas.GetPrimitive('pad_sub_HistWithTimeAxis').GetXaxis()
    xaxis.SetLabelOffset(10)
    taxisfunc.SetYaxisNdivisions(settings_canvas,5,2,0)
    taxisfunc.SetYaxisRanges(settings_canvas,0.001,90)

    return
