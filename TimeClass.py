import time

#------------------------------------------------------------------
class TimeClass :
    def __init__(self) :
        self.StartOfYear = self.TimeFromString("12/31/12 04:00:00")
        self.OneSecond   = self.TimeFromString("12/31/12 04:00:01") - self.StartOfYear
        self.OneMinute   = self.TimeFromString("12/31/12 04:01:00") - self.StartOfYear
        self.OneHour     = self.TimeFromString("12/31/12 05:00:00") - self.StartOfYear
        self.OneDay      = self.TimeFromString("01/01/13 04:00:00") - self.StartOfYear
        self.OneWeek     = self.TimeFromString("01/07/13 04:00:00") - self.StartOfYear
        self.OneYear     = self.TimeFromString("12/31/13 04:00:00") - self.StartOfYear
        self.timerightnow = long(time.mktime(time.localtime()))
        self.MillisecondsInAnHour = 60*60*1000 # 3600000
        
        return

    def WeeksOld(self,universaltime) :
        return (self.timerightnow - universaltime) / self.OneWeek

    def GetWeekOfYear(self,l) :
        # starting from week 0
        l = long(l)
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return (l - self.StartOfYear + is_dst*self.OneHour) / self.OneWeek

    def nWeekToUniversal(self,week) :
        l = self.OneWeek*week + self.StartOfYear
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return l - is_dst*self.OneHour

    def DayWeekToUniversal(self,week,day) :
        return self.nWeekToUniversal(week) + self.OneDay*day

    def GetDayOfWeek(self,l) :
        l = long(l)
        is_dst = time.localtime(l-self.OneHour*4).tm_isdst
        return (l + is_dst*self.OneHour - self.GetWeekOfYear(l)*self.OneWeek - self.StartOfYear) / self.OneDay

    def GetHourOfDay(self,l) :
        l = long(l)
        return time.localtime(l-self.OneHour*4).tm_hour

    def GetTimeOfDay(self,l) :
        # In hours, Starting from 4am
        l = l-self.OneHour*4.
        return time.localtime(l).tm_hour + time.localtime(l).tm_min/60.

    def GetTimeOfDayFromMidnight(self,l) :
        # In hours, Starting from Midnight
        return time.localtime(l).tm_hour + time.localtime(l).tm_min/60.

    def RoundDownToTheHour(self,l) :
        # Round down to nearest hour
        l = long(l)
        return l - self.OneMinute*time.localtime(l).tm_min - self.OneSecond*time.localtime(l).tm_sec

    def TimeFromString(self,s) :
        # universal
        try :
            return long(time.mktime(time.strptime(s, "%m/%d/%y %H:%M:%S")))
        except ValueError :
            try :
                # Tidepool format
                return long(time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%S')))
            except ValueError :
                print 'Error: could not convert to UTC: %s'%(s)
                import sys; sys.exit()
    
    def StringFromTime(self,t,dayonly=False) :
        if dayonly :
            return time.strftime("%m/%d/%y",time.localtime(t))
        return time.strftime("%m/%d/%y %H:%M:%S",time.localtime(t))

    def GetWeekString(self,w) :
        start = time.localtime(self.StartOfYear+self.OneWeek*w)
        end = time.localtime(self.StartOfYear+self.OneWeek*(w+1)-self.OneHour*12)
        return '%s to %s'%(time.strftime('%a, %b %d',start),time.strftime('%a, %b %d',end))

    def GetWeeksString(self,w1,w2) :
        start = time.localtime(self.StartOfYear+self.OneWeek*w1)
        end = time.localtime(self.StartOfYear+self.OneWeek*(w2+1)-self.OneHour*12)
        return '%s to %s'%(time.strftime('%a, %b %d',start),time.strftime('%a, %b %d',end))

    def WeekDayHourToUniversal(self,week,day,hour,minute=0) :
        # Hour after 4am
        return self.nWeekToUniversal(week) + day*self.OneDay + hour*self.OneHour + minute*self.OneMinute

# Do not worry - if you import this file multiple times, you will not create multiple instances.
# The module will be loaded once, and each subsequent "import" will just link the file to
# the static state of the first-imported file.
MyTime = TimeClass()
