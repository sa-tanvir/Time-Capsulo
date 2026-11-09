```python
def __add__(self, other):
    if isinstance(other, relativedelta):
        return self.__class__(years=other.years + self.years,
                              months=other.months + self.months,
                              days=other.days + self.days,
                              hours=other.hours + self.hours,
                              minutes=other.minutes + self.minutes,
                              seconds=other.seconds + self.seconds,
                              microseconds=(other.microseconds +
                                            self.microseconds),
                              leapdays=other.leapdays or self.leapdays,
                              year=(other.year if other.year is not None
                                    else self.year),
                              month=(other.month if other.month is not None
                                     else self.month),
                              day=(other.day if other.day is not None
                                   else self.day),
                              weekday=(other.weekday if other.weekday is not None
                                       else self.weekday),
                              hour=(other.hour if other.hour is not None
                                    else self.hour),
                              minute=(other.minute if other.minute is not None
                                      else self.minute),
                              second=(other.second if other.second is not None
                                      else self.second),
                              microsecond=(other.microsecond
                                           if other.microsecond is not None
                                           else self.microsecond))
    if isinstance(other, datetime.timedelta):
        return self.__class__(years=self.years,
                              months=self.months,
                              days=self.days + other.days,
                              hours=self.hours,
                              minutes=self.minutes,
                              seconds=self.seconds + other.seconds,
                              microseconds=self.microseconds + other.microseconds,
                              leapdays=self.leapdays,
                              year=self.year,
                              month=self.month,
                              day=self.day,
                              weekday=self.weekday,
                              hour=self.hour,
                              minute=self.minute,
                              second=self.second,
                              microsecond=self.microsecond)
    if not isinstance(other, datetime.date):
        return NotImplemented
    elif self._has_time and not isinstance(other, datetime.datetime):
        other = datetime.datetime.fromordinal(other.toordinal())

    year = (self.year or other.year) + self.years
    month = self.month or other.month
    if self.months:
        month += self.months
        if month > 12:
            year += 1
            month -= 12
        elif month < 1:
            year -= 1
            month += 12
    day = min(calendar.monthrange(year, month)[1],
              self.day or other.day)
    repl = {"year": year, "month": month, "day": day}
    for attr in ["hour", "minute", "second", "microsecond"]:
        value = getattr(self, attr)
        if value is not None:
            repl[attr] = value
    days = self.days
    if self.leapdays and month > 2 and calendar.isleap(year):
        days += self.leapdays
    ret = (other.replace(**repl)
           + datetime.timedelta(days=days,
                                hours=self.hours,
                                minutes=self.minutes,
                                seconds=self.seconds,
                                microseconds=self.microseconds))
    if self.weekday:
        weekday, nth = self.weekday.weekday, self.weekday.n or 1
        jumpdays = (abs(nth) - 1) * 7
        if nth > 0:
            jumpdays += (7 - ret.weekday() + weekday) % 7
        else:
            jumpdays += (ret.weekday() - weekday) % 7
            jumpdays *= -1
        ret += datetime.timedelta(days=jumpdays)
    return ret
```
