from BGActionClasses import findFirstBG
from TimeClass import MyTime
import math

#------------------------------------------------------------------
def MakeFoodDeepCopies(containers) :
    import copy

    new_containers = []

    for c in containers :

        if c.IsFood() or c.IsLiverFattyGlucose() :
            # deep-copy food/liver objects so we do not impact the original
            the_copy = copy.deepcopy(c)
            new_containers.append(the_copy)

        else :
            # the same object is fine
            new_containers.append(c)

    return new_containers

#------------------------------------------------------------------
def CalculateResidual(x,containers,settings,list_of_timestamps=[]) :

    # First, link the independent variables x to the containers
    # E.g. [ [1234567,'food'], ['2345678','BGEffect'] ]
    for i in range(len(list_of_timestamps)) :
        iov_0 = list_of_timestamps[i][0]
        attribute = list_of_timestamps[i][1]

        found = False
        for c in containers :
            if (c.iov_0 == iov_0) and hasattr(c,attribute) :
                setattr(c,attribute,x[i])

    # start the estimate of the next point from the first point
    bg_estimate = 0

    residual = 0

    # Work through every bgmeas point
    for bgmeas in containers :

        if not bgmeas.IsMeasurement() :
            continue

        if bgmeas.exclude_ActionRemains :
            continue

        if not bgmeas.firstBG :
            # Moment of truth - Check the residual!
            i_residual = abs(bgmeas.const_BG - bg_estimate)
            #print "Estimate: %.0f Actual: %.0f Residual: %.0f"%(bg_estimate,bgmeas.const_BG,i_residual)
            residual += i_residual

        # start the estimate of the next point from the first point
        bg_estimate = bgmeas.const_BG

        # These better be in chronological order.
        for c in containers :

            # Here, bgmeas.iov_0 and _1 are the times preceding the next meas.
            if c.iov_1 < bgmeas.iov_0_fit :
                continue
            if c.iov_0 > bgmeas.iov_1_fit :
                continue

            if not c.AffectsBG() :
                continue

            # Add the integral from the first BG time up to this time
            bg_estimate += c.getIntegral(bgmeas.iov_0_fit,bgmeas.iov_1_fit,settings)

    # print 'Total residual: %.0f'%(residual)
    return residual

#------------------------------------------------------------------
def BGEffectRemaining(time_ut,containers,settings,abs_value=False) :

    remaining = 0

    for c in containers :
        if not c.AffectsBG() :
            continue
        if c.iov_0 > time_ut :
            continue

        tmp = c.BGEffectRemaining(time_ut,settings)
        if abs_value :
            remaining += abs(tmp)
        else :
            remaining += tmp

    return remaining

#------------------------------------------------------------------
def PrepareBGMeasurementsForFit(containers,settings) :

    # Gather BG points that you want to consider.
    good_bg_conts = []

    # Work through every bgmeas point
    for i_bg in range(len(containers)) :

        bgmeas = containers[i_bg]

        if not bgmeas.IsMeasurement() :
            continue

        bgmeas.iov_0_fit = bgmeas.iov_0
        bgmeas.iov_1_fit = bgmeas.iov_1
        bgmeas.exclude_ActionRemains = False

        remaining = BGEffectRemaining(bgmeas.iov_0,containers,settings)
        remaining_unsigned = BGEffectRemaining(bgmeas.iov_0,containers,settings,abs_value=True)

        # if nothing crazy is going on at the moment, consider this BG measurement.
        #if derivative > 60 or unsigned_derivative > 60 :

        if (not bgmeas.firstBG) and (remaining > 60 or remaining_unsigned > 60) :
            # print 'Skipping %s %d'%(MyTime.StringFromTime(bgmeas.iov_0),bgmeas.const_BG)
            bgmeas.exclude_ActionRemains = True
            i_lastgood = 1
            while True :
                cont_prev = containers[i_bg-i_lastgood]
                if (not cont_prev.IsMeasurement()) or cont_prev.exclude_ActionRemains :
                    i_lastgood += 1
                else :
                    cont_prev.iov_1_fit = bgmeas.iov_1
                    break
        else :
            # print 'Considering %s %d'%(MyTime.StringFromTime(bgmeas.iov_0),bgmeas.const_BG)
            pass

    return

#------------------------------------------------------------------
def MinimizeChi2(c,containers,settings) :

    import numpy as np
    from scipy.optimize import least_squares


    classname = c.__class__.__name__

    itype = {
        'Food':'food',
        'LiverFattyGlucose':'BGEffect',
        }.get(classname)

    x0 = np.array([getattr(c,itype)])
    original = x0[0]

    bounds = {
        'Food'             :([0],[250]),
        'LiverFattyGlucose':([0],[500]),
        }.get(classname)

    list_of_timestamps = [[c.iov_0,itype]]

    res_lsq = least_squares(CalculateResidual, x0, args=(containers,settings,list_of_timestamps),
                            bounds=bounds)

    return

#------------------------------------------------------------------
def MinimizeAllChi2(containers,settings) :
    # Go through food-item-by-food-item and wiggle it until it fits the data.
    # Also consider liver fatty glucose.

    # Do fatty stuff first!
    for c in containers :
    
        if not c.IsLiverFattyGlucose() :
            continue

        MinimizeChi2(c,containers,settings)

    # Should be ordered by time
    for c in containers :
    
        if not c.IsFood() and not c.IsLiverFattyGlucose() :
            continue

        MinimizeChi2(c,containers,settings)

    return None

#------------------------------------------------------------------
def CalculateResidualFoodFatAntiCorrelated(x,fat,food,bg0,bg1,bgs_inbetween,containers,settings) :

    # x[0] is in BGEffect units (mg/dL)
    # x[1] is the food Ta
    # One item is affected positively (fat -> fat + BGEffect), one negatively (food -> food - BGEffect)

    orig_fat  = fat.BGEffect
    orig_food = food.food

    BGSwap = x[0]
    fat.AddBGEffect(bg0.iov_0,bg1.iov_0,settings,BGSwap)
    food.AddBGEffect(bg0.iov_0,bg1.iov_0,settings,-BGSwap)
    food.Ta = x[1]

    # For now, we do not need to add a constraint that bg0 plus the effects equals bg1
    # because we did that in a previous step.

    residual = 0

    for bg in bgs_inbetween :

        # start at bg0 start
        bg_estimate = bg0.const_BG

        for c in containers :
            # Here, bgmeas.iov_0 and _1 are the times preceding the next meas.
            if c.iov_1 < bg0.iov_0 :
                continue
            if c.iov_0 > bg1.iov_0 :
                continue

            if not c.AffectsBG() :
                continue

            # Add the integral from the first BG time up to this time
            bg_estimate += c.getIntegral(bg0.iov_0,bg.iov_0,settings)

        this_residual = abs(bg.const_BG - bg_estimate)
        # print 'During fit: Swap: %d BG: %d Estimate: %d Residual: %d'%(BGSwap,bg.const_BG,bg_estimate,this_residual)
        # loss function is effectively residual^4 now, very punishing for outliers.
        residual += this_residual**2

    # Reset everything
    fat.BGEffect = orig_fat
    food.food = orig_food

    # print 'Total residual: %d'%(residual)
    return residual

#------------------------------------------------------------------
def BalanceFattyEvents(containers,settings) :

    for c_i in range(len(containers)) :

        fat = containers[c_i]

        # Find the fatty event (it better be at night)
        if not fat.IsLiverFattyGlucose() :
            continue

        # print 'Found fatty event at %s'%(MyTime.StringFromTime(fat.iov_0))

        bgs_between = []

        bg_before = None
        for c_j in range(c_i,-1,-1) :
            bgmeas = containers[c_j]
            if not bgmeas.IsMeasurement() :
                continue

            if BGEffectRemaining(bgmeas.iov_0,containers,settings,abs_value=True) > 60 :
                continue

            bg_before = bgmeas
            break

        if not bg_before :
            print 'BalanceFattyEvents: Fat at %s - Cannot find previous measurement -- stopping here.\n'%(MyTime.StringFromTime(fat.iov_0))
            continue

        bg_after = None
        for c_j in range(c_i,len(containers)) :
            meas = containers[c_j]

            if not meas.IsMeasurement() :
                continue
            # Ignore if the measurement is earlier than the "end" of the fat event
            # we added 6 hours to the time_end -- here we subtract 6.
            if meas.iov_0 < (fat.iov_1 - 6*MyTime.OneHour) :
                continue
            bg_after = meas
            break

        if not bg_after :
            print 'BalanceFattyEvents: Fat at %s - Cannot find next measurement -- stopping here.\n'%(MyTime.StringFromTime(fat.iov_0))
            continue

        print 'Fatty Meal Fitter: %s and %s\n'%(MyTime.StringFromTime(bg_before.iov_0),
                                                MyTime.StringFromTime(bg_after.iov_0))

        bgs_inbetween = []
        for c_j in range(containers.index(bg_before)+1,containers.index(bg_after)) :
            if containers[c_j].IsMeasurement() :
                bgs_inbetween.append(containers[c_j])
                # print 'Found BG in between:',containers[c_j].const_BG

        master_food = None

        # Combine the boluses into one super-bolus with a variable Ta
        for c_j in range(len(containers)) :
            food = containers[c_j]
            if not food.IsFood() :
                continue

            # FIX -- need to also account for temp basal!

            # if not ( fat.iov_0 - food.iov_0 ) < 2*MyTime.OneHour :
            #     # < 2 hours before ...
            #     continue

            if not ( food.iov_0 - fat.iov_0 ) < 1.5*MyTime.OneHour :
                # ... and < 1.5 hour after ...
                continue

            if ( food.iov_0 - bg_before.iov_0 ) < 0 :
                # If the food was before the lower-bound BG, do not consider.
                continue

            # print 'Found food item %s %d'%(MyTime.StringFromTime(food.iov_0),food.food)

            # Transfer all the food to the first food item
            if not master_food :
                master_food = food
                master_food.Ta = settings.getFoodTa(master_food.iov_0)
                master_food.fattyMeal = True
            else :
                master_food.food += food.food
                food.food = 0
                food.fattyMeal = True

        # construct a single independent variable that trades BGEffect between FattyGlucose and Food
        # [0] = BGSwap, [1] = Ta
        BGSwap = 0
        Ta = master_food.Ta
        x0 = (BGSwap,Ta)

        BGSwapMin = -fat.getIntegral(bg_before.iov_0,bg_after.iov_0,settings)
        BGSwapMax = master_food.getIntegral(bg_before.iov_0,bg_after.iov_0,settings)
        taMin,taMax = 1,10

        bounds = ([BGSwapMin,taMin],[BGSwapMax,taMax])

        original_food = master_food.food
        original_fat  = fat.BGEffect

        # Define the rules for how the FattyGlucose and the Food are affected by the variable
        # (Not needed yet, because they are already imposed earlier. Maybe later.)

        # Run solve.
        from scipy.optimize import least_squares
        res_lsq = least_squares(CalculateResidualFoodFatAntiCorrelated, x0,
                                args=(fat,master_food,bg_before,bg_after,bgs_inbetween,containers,settings),
                                bounds=bounds)

        # Set the results to the best-fit
        BGSwap = res_lsq.x[0]
        fat.AddBGEffect(        bg_before.iov_0,bg_after.iov_0,settings, BGSwap)
        master_food.AddBGEffect(bg_before.iov_0,bg_after.iov_0,settings,-BGSwap)

    return
