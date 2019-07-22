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

        remaining = 0
        remaining_unsigned = 0
        
        # These better be in chronological order.
        for c in containers :

            try :
                if c.iov_0 > bgmeas.iov_0 :
                    continue
                tmp = c.BGEffectRemaining(bgmeas.iov_0,settings)
                remaining += tmp
                remaining_unsigned += abs(tmp)

            except AttributeError :
                pass

        # if nothing crazy is going on at the moment, consider this BG measurement.
        #if derivative > 60 or unsigned_derivative > 60 :

        if (not bgmeas.firstBG) and (remaining > 60 or remaining_unsigned > 60) :
            print 'Skipping %s %d'%(MyTime.StringFromTime(bgmeas.iov_0),bgmeas.const_BG)
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
            print 'Considering %s %d'%(MyTime.StringFromTime(bgmeas.iov_0),bgmeas.const_BG)
            
    return

#------------------------------------------------------------------
def MinimizeChi2WithFood(containers,settings) :

    import numpy as np
    from scipy.optimize import least_squares

    # Go through food-item-by-food-item and wiggle it until it fits the data.
    # Also consider liver fatty glucose.

    x0 = np.array([0])

    # Do fatty stuff first!
    for c in containers :
    
        if not c.IsLiverFattyGlucose() :
            continue

        itype = 'BGEffect'
        x0[0] = getattr(c,itype)
        original = x0[0]

        bounds = ([0],[500]) # liver BG effect min/max

        list_of_timestamps = [[c.iov_0,itype]]

        res_lsq = least_squares(CalculateResidual, x0, args=(containers,settings,list_of_timestamps),
                                bounds=bounds)

        print 'Result: %s %d -> %d'%(MyTime.StringFromTime(c.iov_0),original,round(res_lsq.x[0],1))

    # Should be ordered by time
    for c in containers :
    
        if not c.IsFood() and not c.IsLiverFattyGlucose() :
            continue

        itype = 'food'
        bounds = ([0],[250]) # in grams

        if c.IsLiverFattyGlucose() :
            itype = 'BGEffect'
            bounds = ([0],[500])

        x0[0] = getattr(c,itype)
        original = x0[0]

        list_of_timestamps = [[c.iov_0,itype]]

        res_lsq = least_squares(CalculateResidual, x0, args=(containers,settings,list_of_timestamps),
                                bounds=bounds)

        print 'Result: %s %d -> %d'%(MyTime.StringFromTime(c.iov_0),original,round(res_lsq.x[0],1))

    return None
