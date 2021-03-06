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

    def Duration_hr(self) :
        return (self.iov_1 - self.iov_0)/float(MyTime.OneHour)

    def AffectsBG(self) :
        try :
            return self.affectsBG
        except AttributeError :
            print 'Please indicate whether %s affects BG!'%(self.__class__.__name__)
            import sys; sys.exit()
        return False

    # Helper functions for figuring out the derived class:
    def IsMeasurement(self) :
        return self.__class__.__name__ == 'BGMeasurement'

    def IsBolus(self) :
        return self.__class__.__name__ == 'InsulinBolus'

    def IsSquareWaveBolus(self) :
        return self.__class__.__name__ == 'SquareWaveBolus'

    def IsDualWaveBolus(self) :
        return self.__class__.__name__ == 'DualWaveBolus'

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

    def IsExercise(self) :
        return self.__class__.__name__ == 'ExerciseEffect'

    def IsLiverFattyGlucose(self) :
        return self.__class__.__name__ == 'LiverFattyGlucose'

    def IsAnnotation(self) :
        return self.__class__.__name__ == 'Annotation'

#------------------------------------------------------------------
class Annotation(BGEventBase) :
    def __init__(self,iov_0,iov_1,annotation) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.annotation = annotation.replace('\x00','').strip()
        return

#------------------------------------------------------------------
class BGActionBase(BGEventBase) :

    def __init__(self,iov_0,iov_1) :
        BGEventBase.__init__(self,iov_0,iov_1)
        return

    def getTa(self,settings,whichTa) :
        if hasattr(self,'Ta') :
            return self.Ta
        return getattr(settings,whichTa)(self.iov_0)

    def getIntegralBase(self,time_start,time_end,settings,whichTa) :
        # whichTa is a string (either 'getInsulinTa' or 'getFoodTa')

        if time_end < self.iov_0 :
            return 0.

        time_hr_start = (time_start - self.iov_0)/float(MyTime.OneHour)
        time_hr_end   = (time_end   - self.iov_0)/float(MyTime.OneHour)

        # Get the appropriate decay time
        Ta = self.getTa(settings,whichTa)

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
        Ta = self.getTa(settings,whichTa)

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
        self.affectsBG = False
        self.const_BG = const_BG # real BG reading
        self.firstBG = False

#------------------------------------------------------------------
class InsulinBolus(BGActionBase) :

    def __init__(self,time_ut,insulin) :
        BGActionBase.__init__(self,time_ut,time_ut + 6.*MyTime.OneHour)
        self.affectsBG = True
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
class SquareWaveBolus(BGEventBase) :

    def __init__(self,time_ut,duration_hr,insulin) :
        BGEventBase.__init__(self,time_ut,time_ut + duration_hr + 6.*MyTime.OneHour)
        self.affectsBG = True
        self.insulin = insulin
        self.duration_hr = duration_hr
        self.miniBoluses = []

        # Update every 6 minutes...!
        time_step_hr = 0.1

        time_it = time_ut

        while time_it < (time_ut + MyTime.OneHour*self.duration_hr) :

            # bolus value is total value divided by number of steps
            bolus_val = self.insulin * time_step_hr / float(self.duration_hr)

            minibolus = InsulinBolus(time_it,bolus_val)
            self.miniBoluses.append(minibolus)
            #print "mini-bolus with %.2f insulin"%(bolus_val)

            # increment by one time step
            time_it += time_step_hr*MyTime.OneHour

        return

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr,settings) :
        return sum(c.getBGEffectDerivPerHourTimesInterval(time_start,delta_hr,settings) for c in self.miniBoluses)

    def getBGEffectDerivPerHour(self,time_ut,settings) :
        return sum(c.getBGEffectDerivPerHour(time_ut,settings) for c in self.miniBoluses)

    def getIntegral(self,time_start,time_end,settings) :
        return sum(c.getIntegral(time_start,time_end,settings) for c in self.miniBoluses)

    def BGEffectRemaining(self,time_ut,settings) :
        return sum(c.BGEffectRemaining(time_ut,settings) for c in self.miniBoluses)

    def Print(self) :
        print 'Square bolus, %s : Duration %.1fh, %2.1fu\n'%(MyTime.StringFromTime(self.iov_0),self.duration_hr,self.insulin)
        return

#------------------------------------------------------------------
class DualWaveBolus(BGEventBase) :

    def __init__(self,time_ut,duration_hr,insulin_square,insulin_inst) :
        BGEventBase.__init__(self,time_ut,time_ut + duration_hr + 6.*MyTime.OneHour)
        self.affectsBG = True
        self.insulin_square = insulin_square
        self.insulin_inst = insulin_inst
        self.duration_hr = duration_hr

        self.square = SquareWaveBolus(time_ut,duration_hr,insulin_square)
        self.inst = InsulinBolus(time_ut,insulin_inst)

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr,settings) :
        return sum(c.getBGEffectDerivPerHourTimesInterval(time_start,delta_hr,settings) for c in [self.square,self.inst])

    def getBGEffectDerivPerHour(self,time_ut,settings) :
        return sum(c.getBGEffectDerivPerHour(time_ut,settings) for c in [self.square,self.inst])

    def getIntegral(self,time_start,time_end,settings) :
        return sum(c.getIntegral(time_start,time_end,settings) for c in [self.square,self.inst])

#------------------------------------------------------------------
class Food(BGActionBase) :

    def __init__(self,iov_0,iov_1,food) :
        BGActionBase.__init__(self,iov_0,iov_1)
        self.affectsBG = True
        self.food = food

        # For eventual suggestions
        self.original_value = food
        self.fattyMeal = False

        return

    def getMagnitudeOfBGEffect(self,settings) :
        return settings.getFoodSensitivity(self.iov_0) * self.food

    def getIntegral(self,time_start,time_end,settings) :
        # If it has its own tA, then the base class knows to override the settings.
        return self.getIntegralBase(time_start,time_end,settings,'getFoodTa')

    # Derivative, useful for making e.g. absorption plots
    def getBGEffectDerivPerHour(self,time_ut,settings) :
        # If it has its own tA, then the base class knows to override the settings.
        return self.getBGEffectDerivPerHourBase(time_ut,settings,'getFoodTa')

    def AddBGEffect(self,time_start,time_end,settings,added_bgeffect) :
        # convert bgeffect into food
        bgeffect_in_slice = self.getIntegral(time_start,time_end,settings)
        # what factor do you need to scale up to the desired effect?
        factor = (bgeffect_in_slice + added_bgeffect)/float(bgeffect_in_slice)
        self.food = self.food * factor

    def PrintSuggestion(self,settings) :
        # We assume that you hijacked this instance to make a fit, and stored
        # the original in "self.original_value"

        if not hasattr(self,'original_value') :
            return

        if not self.fattyMeal :
            # If below a certain threshold, do not bother.
            if self.food > 0 and abs(self.original_value - self.food)/float(self.food) < 0.1 :
                return

            if abs(self.original_value - self.food) < 5 :
                return

        recommendation = ''
        if self.fattyMeal :
            recommendation += '** '
        recommendation += 'Fitted FOOD'
        recommendation += ' at %s'%(MyTime.StringFromTime(self.iov_0))
        recommendation += ' %d -> %d grams'%(self.original_value,self.food)
        if hasattr(self,'Ta') :
            recommendation += ', Ta = %.2f'%(self.Ta)
        print recommendation
        return recommendation

#------------------------------------------------------------------
class LiverBasalGlucose(BGEventBase) :
    # This one is a bit special, since its effect is driven entirely
    # by the setting LiverHourlyGlucose, and it's a PARAMETER OF INTEREST.
    # - It has an "infinite" (or undefined) magnitude
    # - It has no defined start time, so its integral can only be defined between two moments

    def __init__(self) :
        BGEventBase.__init__(self,0,float('inf'))
        self.affectsBG = True
        self.binWidth_hr = 0.25 # granularity of the binning, when calculating.
        self.nBins = int( 24 / self.binWidth_hr )
        self.LiverHourlyGlucoseFine = [0]*self.nBins # Make memory slots, but recalculate each time
        self.smear_hr_pm = 1 # average the rate over plus or minus X hours
        return

    def getBin(self,time_ut) :
        bin = int(MyTime.GetTimeOfDay(time_ut)/float(self.binWidth_hr))
        return bin

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

        # iterators (both are incremented, to avoid float-to-int errors)
        it_time = time_start
        liver_bin = self.getBin(it_time)

        time_start_day_4am = MyTime.RoundDownToTheDay(time_start)

        # print 'Getting integral for',MyTime.StringFromTime(time_start),MyTime.StringFromTime(time_end)

        # Go through times up to the end, plus one bin width (in order to avoid missing the last bin)
        while (it_time <= time_end + self.binWidth_hr*MyTime.OneHour) :

            # For each bin, find the valid time interval (in hours)
            # This should ensure that the final bin is treated correctly.
            low_edge = max(time_start,time_start_day_4am + liver_bin    *self.binWidth_hr*MyTime.OneHour)
            up_edge  = min(time_end  ,time_start_day_4am + (liver_bin+1)*self.binWidth_hr*MyTime.OneHour)

            if up_edge < low_edge :
                break

            delta_time_hr = (up_edge - low_edge)/float(MyTime.OneHour)
            # print 'bin edges:',MyTime.StringFromTime(time_start_day_4am + liver_bin    *self.binWidth_hr*MyTime.OneHour),
            # print              MyTime.StringFromTime(time_start_day_4am + (liver_bin+1)*self.binWidth_hr*MyTime.OneHour)
            # print MyTime.StringFromTime(low_edge), MyTime.StringFromTime(up_edge), delta_time_hr

            # return (Glucose / hour) * D(hour)
            sum += delta_time_hr * tmp_LiverHourlyGlucoseFine[liver_bin % self.nBins]

            it_time += self.binWidth_hr*MyTime.OneHour
            liver_bin += 1

        return sum

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

    def __init__(self,iov_0,iov_1,h_basal,h_insulin=[],containers=[]) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.affectsBG = True
        self.BasalRates = [0]*48
        HistToList(h_basal,self.BasalRates)

        # Insulin sensitivity is needed to make liver events
        tmp_InsulinSensitivityList = [0]*48
        if h_insulin :
            HistToList(h_insulin,tmp_InsulinSensitivityList)

        self.basalBoluses = []
        time_ut = MyTime.RoundDownToTheHour(iov_0)

        # Update every 6 minutes...!
        time_step_hr = 0.1

        fattyEvents = dict()

        while time_ut < iov_1 :

            basalFactor = 1
            bolus_val = self.BasalRates[self.getBin(time_ut)]*float(time_step_hr)*basalFactor
            insulin_sensi = tmp_InsulinSensitivityList[self.getBin(time_ut)]

            # If there is a TempBasal, then modify the basalFactor
            for c in containers :
                if not c.IsTempBasal() :
                    continue

                if c.iov_0 > time_ut or time_ut > c.iov_1 :
                    continue

                basalFactor = c.basalFactor

                # If the basalFactor >1, then
                # Make a new LiverFattyGlucose object, add it to container list
                if basalFactor > 1 :
                    bolusSlice = insulin_sensi*bolus_val*(basalFactor-1)

                    if c.iov_0 not in fattyEvents.keys() :
                        Ta_tempBasal = (c.iov_1 - c.iov_0) / float(MyTime.OneHour)
                        fattyEvents[c.iov_0] = {'iov_0':c.iov_0,'iov_1':c.iov_1}
                        fattyEvents[c.iov_0]['BGEffect'] = bolusSlice
                        fattyEvents[c.iov_0]['Ta_tempBasal'] = Ta_tempBasal
                        fattyEvents[c.iov_0]['fractionOfBasal'] = basalFactor-1
                    else :
                        fattyEvents[c.iov_0]['BGEffect'] += bolusSlice

            # Now check for Suspend, which should preempt TempBasals
            for c in containers :
                if not c.IsSuspend() :
                    continue
                if c.iov_0 < time_ut and time_ut < c.iov_1 :
                    basalFactor = c.basalFactor

            # Finally, make the mini-bolus for the basal insulin.
            bolus_val *= basalFactor
            minibolus = InsulinBolus(time_ut,bolus_val)
            self.basalBoluses.append(minibolus)

            time_ut += time_step_hr*MyTime.OneHour

        for k in fattyEvents.keys() :
            fe = fattyEvents[k]
            fattyEvent = LiverFattyGlucose(fe['iov_0'],fe['iov_1'],fe['BGEffect'],fe['Ta_tempBasal'],fe['fractionOfBasal'])
            fattyEvent.Print()
            containers.append(fattyEvent)

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
        self.affectsBG = False
        self.basalFactor = basalFactor

#------------------------------------------------------------------
class Suspend(TempBasal) :

    # Very similar to TempBasal, except that we need a different class
    # because Suspend takes precedence over TempBasal

    def __init__(self,iov_0,iov_1) :
        TempBasal.__init__(self,iov_0,iov_1,0)
        self.affectsBG = False

#------------------------------------------------------------------
class LiverFattyGlucose(BGActionBase) :
    #
    # This assumes that the independent variable that the user keeps track of
    # is simply "BG Effect". In other words, we will not attempt any tricky transformation
    # to insulin or food or something.

    def __init__(self,time_start,time_end,BGEffect,Ta_tempBasal,fractionOfBasal) :
        BGActionBase.__init__(self,time_start,time_end + 6.*MyTime.OneHour)
        self.affectsBG = True

        # We keep track of this only in terms of BG effect.
        # When created, this comes from the insulin * sensitivity. But then it becomes
        # a non-associated object (i.e. not dependent on any settings).
        # If a mis-bolus is made, then the magnitude of the mis-bolus is calculated in BG points,
        # and then translated back to insulin via the sensitivity setting.
        self.BGEffect = BGEffect

        # For eventual suggestions
        self.original_value = BGEffect
        self.fractionOfBasal = fractionOfBasal

        # It also has its own Ta
        # This is tunable (1.4 works ok for a 6-hr basal)
        self.Ta_tempBasal = Ta_tempBasal
        self.Ta = Ta_tempBasal * 1.4

        return

    def getFattyGlucoseLocalTa(self,time_ut) :
        return self.Ta

    def getMagnitudeOfBGEffect(self,settings) :
        # settings is not used
        return self.BGEffect

    def getIntegral(self,time_start,time_end,settings) :

        # Use a trick below: instead of settings, give them self (for Ta)
        return self.getIntegralBase(time_start,time_end,self,'getFattyGlucoseLocalTa')


    # Derivative, useful for making e.g. absorption plots
    def getBGEffectDerivPerHour(self,time_ut,settings) :

        # Use a trick below: instead of settings, give them self (for Ta)
        return self.getBGEffectDerivPerHourBase(time_ut,self,'getFattyGlucoseLocalTa')

    def AddBGEffect(self,time_start,time_end,settings,added_bgeffect) :
        # add a bgeffect (in a given time slice)
        bgeffect_in_slice = self.getIntegral(time_start,time_end,settings)
        factor = (bgeffect_in_slice + added_bgeffect)/float(bgeffect_in_slice)
        self.BGEffect = self.BGEffect * factor

    def Print(self) :
        cout = 'LiverFattyGlucose:'
        cout += ' %s -'%(MyTime.StringFromTime(self.iov_0))
        cout += ' %s,' %(MyTime.StringFromTime(self.iov_1))
        bg = ('%.0f'%(self.BGEffect)).rjust(3)
        cout += ' BGEffect: %s mg/dL, lifetime: %2.1f'%(bg,self.Ta)
        print cout + '\n'
        return

    def PrintSuggestion(self,settings) :
        # We assume that you hijacked this instance to make a fit, and stored
        # the original in "self.original_value"

        if not hasattr(self,'original_value') :
            return

        # If below a certain threshold, do not bother.
        if abs(self.original_value - self.BGEffect)/float(self.BGEffect) < 0.1 :
            return

        Sfood = float(settings.getFoodSensitivity(self.iov_0))
        tempBasal_old = 100*(1 + self.fractionOfBasal)
        tempBasal_new = 100*(1 + (self.fractionOfBasal * self.BGEffect/float(self.original_value) ) )
        recommendation = '** Recommend TEMP BASAL'
        recommendation += ' at %s'%(MyTime.StringFromTime(self.iov_0))
        recommendation += ' %d -> %d mgdL'%(self.original_value,self.BGEffect)
        recommendation += ' (%d -> %d grams)'%(self.original_value/Sfood,self.BGEffect/Sfood)
        recommendation += ' (%d%% -> %d%% for %.2f hours)'%(tempBasal_old,tempBasal_new,self.Ta_tempBasal)
        print recommendation
        return recommendation

#------------------------------------------------------------------
class ExerciseEffect(BGEventBase) :
    #
    # This will calculate the "multiplier effect" that exercise has on insulin,
    # and its effect is the sum of those effects.
    #
    def __init__(self,iov_0,iov_1,factor,containers=[]) :
        BGEventBase.__init__(self,iov_0,iov_1)
        self.affectsBG = True
        self.factor = factor
        self.affectedEvents = []
        if len(containers) :
            self.LoadContainers(containers)
        return

    def LoadContainers(self,containers) :
        for c in containers :
            if c.iov_0 > self.iov_1 :
                continue

            if c.iov_1 < self.iov_0 :
                continue

            # Consider only insulin
            if not (c.IsBasalInsulin() or c.IsBolus()) :
                continue

            self.affectedEvents.append(c)

        return

    def BGEffectRemaining(self,the_time,settings) :
        return 0

    def getMagnitudeOfBGEffect(self,settings) :
        mag = 0

        time_step = self.iov_0
        hours_per_step = 0.1

        while time_step < self.iov_1 :

            for c in self.affectedEvents :
                mag += c.getBGEffectDerivPerHourTimesInterval(time_step,hours_per_step,settings)

            time_step += (hours_per_step * MyTime.OneHour)

        return mag * self.factor

    def getBGEffectDerivPerHour(self,time_ut,settings) :
        deriv = 0
        if self.iov_0 > time_ut or time_ut > self.iov_1 :
            return 0

        for c in self.affectedEvents :
            deriv += c.getBGEffectDerivPerHour(time_ut,settings)

        return deriv * self.factor

    def getBGEffectDerivPerHourTimesInterval(self,time_start,delta_hr,settings) :
        ret = 0
        if self.iov_0 > time_start or time_start > self.iov_1 :
            return 0

        for c in self.affectedEvents :
            ret += c.getBGEffectDerivPerHourTimesInterval(time_start,delta_hr,settings)

        return ret * self.factor

    def getIntegral(self,time_start,time_end,settings) :

        ret = 0
        if self.iov_0 > time_start or time_end > self.iov_1 :
            return 0

        for c in self.affectedEvents :
            ret += c.getIntegral(time_start,time_end,settings)

        return ret * self.factor
