import time

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class TimeClass :
    def __init__(self) :
        self.StartOfYear = self.TimeFromString("12/31/12 04:00:00")
        self.OneSecond   = self.TimeFromString("12/31/12 04:00:01") - self.StartOfYear
        self.OneMinute   = self.TimeFromString("12/31/12 04:01:00") - self.StartOfYear
        self.OneHour     = self.TimeFromString("12/31/12 05:00:00") - self.StartOfYear
        self.OneDay      = self.TimeFromString("01/01/13 04:00:00") - self.StartOfYear
        self.OneWeek     = self.TimeFromString("01/07/13 04:00:00") - self.StartOfYear
        self.OneYear     = self.TimeFromString("12/31/13 04:00:00") - self.StartOfYear
        
        return

    def GetWeekOfYear(self,l) :
        # starting from week 0
        l = long(l)
        l = l + self.DSTCorr(l)
        return (l - self.StartOfYear) / self.OneWeek

    def GetDayOfWeek(self,l) :
        l = long(l)
        l = l + self.DSTCorr(l)
        return (l - self.GetWeekOfYear(l)*self.OneWeek - self.StartOfYear) / self.OneDay

    def GetHourOfDay(self,l) :
        l = long(l)
        l = l + self.DSTCorr(l)
        return (l - self.GetWeekOfYear(l)*self.OneWeek - self.GetDayOfWeek(l)*self.OneDay - self.StartOfYear) / self.OneHour

    def GetTimeOfDay(self,l) :
        # Starting from 4am
        l = l + self.DSTCorr(l)
        return (l - self.GetWeekOfYear(l)*self.OneWeek - self.GetDayOfWeek(l)*self.OneDay - self.StartOfYear) / float(self.OneHour)

    def DSTCorr(self,l) :
        return self.OneHour if l > self.TimeFromString("03/31/13 03:00:00") else 0

    def TimeFromString(self,s) :
        # universal
        return long(time.mktime(time.strptime(s, "%m/%d/%y %H:%M:%S")))
    
    def StringFromTime(self,t) :
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
        l = self.StartOfYear + week*self.OneWeek + day*self.OneDay + hour*self.OneHour + minute*self.OneMinute
        l = l - self.DSTCorr(l)
        return l
