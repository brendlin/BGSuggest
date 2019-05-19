import math
from TimeClass import MyTime

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

    def __init__(self,iov_0,iov_1,insulin) :
        BGActionBase.__init__(self,iov_0,iov_1)
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
    # by the setting LiverHourlyGlucose.
    # - It has an "infinite" (or undefined) magnitude
    # - It has no defined start time, so its integral can only be defined between two moments

    def __init__(self) :
        BGEventBase.__init__(self,0,float('inf'))
        return

    def getIntegral(self,time_start,time_end,settings) :

        sum = 0

        # consider all overlapping bins
        for i in range(settings.getBin(time_start),settings.getBin(time_end)+1) :

            # For each bin, find the valid time interval
            # This should ensure that the final bin is treated correctly.
            low_edge = max(time_start,binLowEdge)
            up_edge  = min(time_end  ,time_end  )

            delta_time = up_edge - low_edge

            # return (Glucose / hour) * D(hour)
            sum += delta_time * settings.LiverHourlyGlucose[i]

        return sum

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr) :

        # Yeah this is really just the integral.
        return self.getIntegral(time_start,time_start + delta_hr*MyTime.OneHour)

    def getBGEffectDerivPerHour(self,time_ut,settings) :

        # just a wrapper for the true user setting
        return settings.getLiverHourlyGlucose(time_ut)
