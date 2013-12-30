from PlotMacro import WeekPlot,t,BGFunction
from ROOT import TCanvas
c = WeekPlot()
#c.SuppliesSummary()
c.Detailed('last')
c.Overview('last')
c.YearInReview()
#c.DoSample()

