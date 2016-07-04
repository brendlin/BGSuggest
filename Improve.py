from PlotMacro import WeekPlot,t,BGFunction
import ROOT
from YearInReview import YearInReview
import pennSoftLepton.PlotFunctions as plotfunc
from SampleEarlyBolus import SampleEarlyBolus
from SuppliesSummary import SuppliesSummary
from PyBGSuggestHelpers import PredictionCanvas

def main(options,args) :

    plotfunc.SetupStyle()

    f = ROOT.TFile('output_all.root')
    e = f.Get('LongTerm')
    
    f_shortterm = ROOT.TFile('output.root')
    e_shortterm = f_shortterm.Get('Tree Name')

    canvases = []

#     c = WeekPlot()

#     if options.detailed :
#         c.Detailed('last')
#     if options.overview :
#         c.Overview('last')

    if options.detailed :
        canvases.append(PredictionCanvas(e_shortterm,options.day_of_week,-options.week,rootfile=f_shortterm))
    if options.yir :
        canvases.append(YearInReview(e))
    if options.example :
        canvases.append(SampleEarlyBolus())
    if False :
        rewind,supplies,test_frequency = SuppliesSummary(e)
    
    
    raw_input('Pausing. Press enter to exit.')

    if options.save :
        for i in canvases :
            i.Print(i.GetName()+'.pdf')
            i.Print(i.GetName()+'.eps')
    return

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--save',action='store_true',default=False,dest='save',help='save cans to pdf')
    p.add_option('--detailed',action='store_true',default=False,dest='detailed',help='save cans to pdf')
    p.add_option('--overview',action='store_true',default=False,dest='overview',help='save cans to pdf')
    p.add_option('--yir',action='store_true',default=False,dest='yir',help='save cans to pdf')
    p.add_option('--example',action='store_true',default=False,dest='example',help='save cans to pdf')
    p.add_option('--m' ,action='store_true',default=False,dest='m' ,help='Monday')
    p.add_option('--t' ,action='store_true',default=False,dest='t' ,help='Tuesday')
    p.add_option('--w' ,action='store_true',default=False,dest='w' ,help='Wednesday')
    p.add_option('--th',action='store_true',default=False,dest='th',help='Thursday')
    p.add_option('--f' ,action='store_true',default=False,dest='f' ,help='Friday')
    p.add_option('--s' ,action='store_true',default=False,dest='s' ,help='Saturday')
    p.add_option('--su',action='store_true',default=False,dest='su',help='Sunday')
    p.add_option('--week',type='int',default=0,dest='week',help='Number of weeks ago (0)')
    options,args = p.parse_args()

    options.day_of_week = -1
    if options.m  : options.day_of_week = 0
    if options.t  : options.day_of_week = 1
    if options.w  : options.day_of_week = 2
    if options.th : options.day_of_week = 3
    if options.f  : options.day_of_week = 4
    if options.s  : options.day_of_week = 5
    if options.su : options.day_of_week = 6

    if options.detailed and options.day_of_week < 0 :
        print 'Error! Please specify day (e.g. --m). Exiting.'
        import sys
        sys.exit()

    main(options,args)
