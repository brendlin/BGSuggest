import math
from TimeClass import MyTime
from Settings import HistToList

#------------------------------------------------------------------
def InsulinActionCurve(time_hr,Ta) :
    if time_hr < 0 :
        return 0

    result = 1 - math.pow(0.05,math.pow(time_hr/float(Ta),2))
    return result

#------------------------------------------------------------------
def InsulinActionCurveDerivative(time_hr,Ta) :
    if time_hr < 0 :
        return 0

    result = math.log(20)*2*math.pow((1/float(Ta)),2)
    result *= time_hr
    result *= math.pow(0.05,math.pow(time_hr/float(Ta),2))
    return result

#------------------------------------------------------------------
def findFirstBG(conts) :
    # Quick function to find the first BG
    for c in conts :
        if c.IsMeasurement() and c.firstBG :
            return c
    return None

#------------------------------------------------------------------
class BGEventBase :
    
    def __init__(self,iov_0,iov_1) :
        self.iov_0 = iov_0 # ut
        self.iov_1 = iov_1 # ut
        return

    # Helper functions for figuring out the derived class:
    def IsMeasurement(self) :
        return self.__class__.__name__ == 'BGMeasurement'

    def IsBolus(self) :
        return self.__class__.__name__ == 'InsulinBolus'

    def IsFood(self) :
        return self.__class__.__name__ == 'Food'

    def IsBasalGlucose(self) :
        return self.__class__.__name__ == 'LiverBasalGlucose'

    def IsBasalInsulin(self) :
        return self.__class__.__name__ == 'BasalInsulin'

    def IsTempBasal(self) :
        return self.__class__.__name__ == 'TempBasal'

    def IsSuspend(self) :
        return self.__class__.__name__ == 'Suspend'

#------------------------------------------------------------------
class BGActionBase(BGEventBase) :

    def __init__(self,iov_0,iov_1) :
        BGEventBase.__init__(self,iov_0,iov_1)
        return

    def getIntegralBase(self,time_start,time_end,settings,whichTa) :
        # whichTa is a string (either 'getInsulinTa' or 'getFoodTa')

        if time_end < self.iov_0 :
            return 0.

        time_hr_start = (time_start - self.iov_0)/float(MyTime.OneHour)
        time_hr_end   = (time_end   - self.iov_0)/float(MyTime.OneHour)

        # Get the appropriate decay time
        Ta = getattr(settings,whichTa)(self.iov_0)

        # Get the magnitude (virtual, must be specified by the derived class)
        magnitude = self.getMagnitudeOfBGEffect(settings)

        return (InsulinActionCurve(time_hr_end,Ta) - InsulinActionCurve(time_hr_start,Ta)) * magnitude


    # The BG equivalent of "Active Insulin"
    def BGEffectRemaining(self,time_ut,settings) :
        
        infinity = time_ut+MyTime.OneYear

        # getIntegral is virtual, specified in the derived class
        return self.getIntegral(time_ut,infinity,settings)


    # Derivative, useful for making e.g. absorption plots
    def getBGEffectDerivPerHourBase(self,time_ut,settings,whichTa) :

        if (time_ut < self.iov_0) or (time_ut > self.iov_1) :
            return 0.

        time_hr = (time_ut-self.iov_0)/float(MyTime.OneHour)
        Ta = getattr(settings,whichTa)(self.iov_0)

        return InsulinActionCurveDerivative(time_hr,Ta) * self.getMagnitudeOfBGEffect(settings)

    # TODO: just replace this with the integral, no???
    def getBGEffectDerivPerHourTimesInterval(self,time_ut,delta_hr,settings) :
        return self.getBGEffectDerivPerHour(time_ut,settings) * delta_hr


#------------------------------------------------------------------
class BGMeasurement(BGEventBase) :
    #
    # BG Reading
    #
    def __init__(self,iov_0,iov_1,const_BG) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.const_BG = const_BG # real BG reading
        self.firstBG = False

#------------------------------------------------------------------
class InsulinBolus(BGActionBase) :

    def __init__(self,time_ut,insulin) :
        BGActionBase.__init__(self,time_ut,time_ut + 6.*MyTime.OneHour)
        self.insulin = insulin
        self.UserInputCarbSensitivity = 2
        self.BWZMatchedDelivered = True
        self.BWZEstimate = 0
        self.BWZInsulinSensitivity = 0
        self.BWZCorrectionEstimate = 0
        self.BWZFoodEstimate       = 0
        self.BWZActiveInsulin      = 0
        self.BWZBGInput            = 0
        self.BWZCarbRatio          = 0

    # This used to be called getEffectiveSensitivity, but that name is misleading for food.
    def getMagnitudeOfBGEffect(self,settings) :
        return settings.getInsulinSensitivity(self.iov_0) * self.insulin

    def getIntegral(self,time_start,time_end,settings) :
        return self.getIntegralBase(time_start,time_end,settings,'getInsulinTa')

    # Derivative, useful for making e.g. absorption plots
    def getBGEffectDerivPerHour(self,time_ut,settings) :
        return self.getBGEffectDerivPerHourBase(time_ut,settings,'getInsulinTa')

    def PrintBolus(self) :

        star = ' *' if not self.BWZMatchedDelivered else ''
        decaytime = ' %d hour decay'%(self.UserInputCarbSensitivity) if (self.UserInputCarbSensitivity > 2) else ''
        print 'Bolus, %s (input BG: %d mg/dl) (S=%d)'%(MyTime.StringFromTime(self.iov_0),self.BWZBGInput,self.BWZInsulinSensitivity)

        def PrintDetails(title,item,postscript='') :
            print title + ('%2.1f u;'%(item)).rjust(10)+(' %2.1f mg/dl'%(item*self.BWZInsulinSensitivity)).rjust(15)+(' %2.1f g'%(item*self.BWZCarbRatio)).rjust(10)+postscript
            return

        PrintDetails('  Total Delivered insulin : ',self.insulin,star)
        PrintDetails('  Total Suggested insulin : ',self.BWZEstimate)
        PrintDetails('             food insulin : ',self.BWZFoodEstimate,decaytime)
        PrintDetails('       correction insulin : ',self.BWZCorrectionEstimate)
        PrintDetails('           active insulin : ',self.BWZActiveInsulin)
        print

        return

#------------------------------------------------------------------
class Food(BGActionBase) :

    def __init__(self,iov_0,iov_1,food) :
        BGActionBase.__init__(self,iov_0,iov_1)
        self.food = food

    def getMagnitudeOfBGEffect(self,settings) :
        return settings.getFoodSensitivity(self.iov_0) * self.food

    def getIntegral(self,time_start,time_end,settings) :
        return self.getIntegralBase(time_start,time_end,settings,'getFoodTa')

    # Derivative, useful for making e.g. absorption plots
    def getBGEffectDerivPerHour(self,time_ut,settings) :
        return self.getBGEffectDerivPerHourBase(time_ut,settings,'getFoodTa')

#------------------------------------------------------------------
class LiverBasalGlucose(BGEventBase) :
    # This one is a bit special, since its effect is driven entirely
    # by the setting LiverHourlyGlucose, and it's a PARAMETER OF INTEREST.
    # - It has an "infinite" (or undefined) magnitude
    # - It has no defined start time, so its integral can only be defined between two moments

    def __init__(self) :
        BGEventBase.__init__(self,0,float('inf'))
        self.binWidth_hr = 0.25 # granularity of the binning, when calculating.
        self.nBins = int( 24 / self.binWidth_hr )
        self.LiverHourlyGlucoseFine = [0]*self.nBins # Make memory slots, but recalculate each time
        self.smear_hr_pm = 1 # average the rate over plus or minus X hours
        return

    def getBin(self) :
        return int(MyTime.GetTimeOfDay(time_ut)/self.binWidth_hr)

    def getSmearedList(self,settings) :
        # First, lengthen the list
        tmp = []
        for BG in settings.LiverHourlyGlucose :
            for j in range(int(settings.binWidth_hr/self.binWidth_hr)) :
                tmp.append(BG)

        # Now, smear it:
        smear_hr_pm = int(self.smear_hr_pm/self.binWidth_hr)
        for i in range(len(tmp)) :
            n = 0
            val = 0
            for j in range(i-smear_hr_pm,i+smear_hr_pm+1) :
                n += 1
                val += tmp[j%(len(tmp))]
            self.LiverHourlyGlucoseFine[i] = val/float(n)

        #print ''.join('%2.1f '%(a) for a in LiverHourlyGlucoseFine)
        return self.LiverHourlyGlucoseFine


    def getIntegral(self,time_start,time_end,settings) :

        tmp_LiverHourlyGlucoseFine = self.getSmearedList(settings)

        sum = 0

        # consider all overlapping bins
        for i in range(self.getBin(time_start),self.getBin(time_end)+1) :

            # For each bin, find the valid time interval (in hours)
            # This should ensure that the final bin is treated correctly.
            low_edge = max(MyTime.GetTimeOfDay(time_start),i*self.binWidth_hr)
            up_edge  = min(MyTime.GetTimeOfDay(time_end)  ,(i+1)*self.binWidth_hr)

            delta_time = up_edge - low_edge

            # return (Glucose / hour) * D(hour)
            sum += delta_time * tmp_LiverHourlyGlucoseFine[i]

        return sum

    def getBin(self,time_ut) :
        bin = int(MyTime.GetTimeOfDay(time_ut)/float(self.binWidth_hr))
        return bin

    def BGEffectRemaining(self,the_time,settings) :
        return 0

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr,settings) :

        # Yeah this is really just the integral.
        return self.getIntegral(time_start,time_start + delta_hr*MyTime.OneHour,settings)

    def getBGEffectDerivPerHour(self,time_ut,settings) :

        # just a wrapper for the true user setting
        #return settings.getLiverHourlyGlucose(time_ut)

        # Same, but for the smeared list:
        return self.getSmearedList(settings)[self.getBin(time_ut)]


#------------------------------------------------------------------
class BasalInsulin(BGEventBase) :
    # This is driven by the basal settings, but it is NOT a parameter of interest, it is a known
    # quantity. But it has some similarities to LiverBasalGlucose:
    # - It has an "infinite" (or undefined) magnitude
    # - It has no defined start time, so its integral can only be defined between two moments

    def getBin(self,time_ut) :
        # From 4am ... and assuming 48 bins
        return int(2*MyTime.GetTimeOfDay(time_ut))

    def __init__(self,iov_0,iov_1,h_basal,containers=[]) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.BasalRates = [0]*48
        HistToList(h_basal,self.BasalRates)

        self.basalBoluses = []
        time_ut = MyTime.RoundDownToTheHour(iov_0)

        # Update every 6 minutes...!
        time_step_hr = 0.1

        while time_ut < iov_1 :

            basalFactor = 1

            # If there is a TempBasal, then modify the basalFactor
            for c in containers :
                if not c.IsTempBasal() :
                    continue
                if c.iov_0 < time_ut and time_ut < c.iov_1 :
                    basalFactor = c.basalFactor

            # Now check for Suspend, which should preempt TempBasals
            for c in containers :
                if not c.IsSuspend() :
                    continue
                if c.iov_0 < time_ut and time_ut < c.iov_1 :
                    basalFactor = c.basalFactor

            bolus_val = self.BasalRates[self.getBin(time_ut)]*float(time_step_hr)*basalFactor
            minibolus = InsulinBolus(time_ut,bolus_val)
            self.basalBoluses.append(minibolus)

            time_ut += time_step_hr*MyTime.OneHour

        return

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr,settings) :
        return sum(c.getBGEffectDerivPerHourTimesInterval(time_start,delta_hr,settings) for c in self.basalBoluses)

    def getBGEffectDerivPerHour(self,time_ut,settings) :
        return sum(c.getBGEffectDerivPerHour(time_ut,settings) for c in self.basalBoluses)

    def getIntegral(self,time_start,time_end,settings) :
        return sum(c.getIntegral(time_start,time_end,settings) for c in self.basalBoluses)

    def BGEffectRemaining(self,the_time,settings) :
        return 0

#------------------------------------------------------------------
class TempBasal(BGEventBase) :

    # This class is designed to communicate with the BasalInsulin class.

    def __init__(self,iov_0,iov_1,basalFactor) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.basalFactor = basalFactor

#------------------------------------------------------------------
class Suspend(TempBasal) :

    # Very similar to TempBasal, except that we need a different class
    # because Suspend takes precedence over TempBasal

    def __init__(self,iov_0,iov_1) :
        TempBasal.__init__(self,iov_0,iov_1,0)
