import ROOT

#
# This is meant to store a list of settings histograms, with the day starting from 4am.
# 
#
class SettingsHistograms :

    def __init__(self,_type_of_hist) :
        self.hist_list = []
        self.type_of_hist = _type_of_hist
        return

    def latestHistogram(self) :
        if not self.hist_list :
            print 'warning! No insulin-carb ratio on record!'
        else :
            return self.hist_list[-1]

        return None

    def getOrMakeHistogram(self,histo_tag) :

        # Get the latest histogram, if it exists
        for hist in self.hist_list :
            if histo_tag in hist.GetName() :
                return hist

        # If it does not exist, make a new one:
        # They are all half-hour increments, starting from 4am!
        hist = ROOT.TH1F('%s %s'%(self.type_of_hist,histo_tag),histo_tag,48,0,24)
        hist.SetDirectory(0)

        # append the new histogram to the list
        self.hist_list.append(hist)

        return hist


    def WriteToFile(self,rootfile) :

        if not rootfile :
            return

        def HistsAreIdentical(h1,h2) :
            identical = True
            for i in range(h1.GetNbinsX()+2) :
                if h1.GetBinContent(i) != h2.GetBinContent(i) :
                    identical = False
            return identical

        for i in range(len(self.hist_list)) :
            if not i :
                continue
            if HistsAreIdentical(self.hist_list[i],self.hist_list[i-1]) :
                self.hist_list[i].SetTitle('skip')

        for i in reversed(self.hist_list) :
            if i.GetTitle() == 'skip' :
                continue
            rootfile.cd()
            i.Write()
        return


    def AddSettingToHistogram(self,histo_tag,timeOfDay_midnight,value) :
        # The input, timeOfDay, is in hours (float), starting from MIDNIGHT
        # but it will be CONVERTED to 4am

        hist = self.getOrMakeHistogram(histo_tag)

        # hour -> half hour increments
        timeOfDay_midnight = int(2*int(timeOfDay_midnight))

        # half hour increments, 12am to 4am start time conversion:
        timeOfDay_midnight = int(timeOfDay_midnight)
        timeOfDay = timeOfDay_midnight - 8 

        # Roll pre-4am to the end of the histogram.
        if timeOfDay < 0 :
            timeOfDay = timeOfDay + 48 # half hour increments

        hist.SetBinContent(timeOfDay+1,value)
        return


    def GetSettingFromHistogram(self,timeOfDay) :
        # The input, timeOfDay, is in hours (float), starting from 4am
        # convert to bins - because these histograms go from 0 to 24.

        hist = self.latestHistogram()

        if not hist :
            'Missing histogram - exiting.'
            import sys; sys.exit;

        iterator = 0.
        while True :
            bin = hist.FindBin(timeOfDay-iterator)
            if bin == 0 :
                iterator -= 24

            # Both the input and the histogram start from 4am.
            result = hist.GetBinContent(bin)
            #print 'timeOfDay:',timeOfDay,'iterator:',iterator,'bin:',hist.FindBin(timeOfDay-iterator),'result:',result

            # Return a non-zero result.
            if result > 0 :
                return result

            # If a result is zero, look back another half hour...
            iterator += 0.5

        return 0
