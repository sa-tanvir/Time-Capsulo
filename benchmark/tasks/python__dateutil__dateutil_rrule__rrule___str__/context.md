# Context for the function to implement

- **Language:** python
- **File:** `dateutil/rrule.py`
- **Enclosing scope:** `class rrule(rrulebase)`

## Imports / includes available in this file

```
import itertools
import datetime
import calendar
import re
import sys
from six import advance_iterator, integer_types
from six.moves import _thread, range
import heapq
from ._common import weekday as weekdaybase
from warnings import warn
```

## Other functions defined in the same file (signatures only; you may call them)

```
__construct_byset( self , start , byxxx , base )
__mod_distance( self , value , byxxx , base )
_handle_BYWEEKDAY( self , rrkwargs , name , value , ** kwargs )
_handle_FREQ( self , rrkwargs , name , value , ** kwargs )
_handle_UNTIL( self , rrkwargs , name , value , ** kwargs )
_handle_WKST( self , rrkwargs , name , value , ** kwargs )
_handle_int( self , rrkwargs , name , value , ** kwargs )
_handle_int_list( self , rrkwargs , name , value , ** kwargs )
_invalidate_cache( self )
_invalidates_cache( f )
_invalidates_cache.inner_func( self , * args , ** kwargs )
_iter( self )
_iter_cached( self )
_parse_date_value( self , date_value , parms , rule_tzids , ignoretz , tzids , tzinfos )
_parse_rfc( self , s , dtstart = None , cache = False , unfold = False , forceset = False , compatible = False , ignoretz = False , tzids = None , tzinfos = None )
_parse_rfc_rrule( self , line , dtstart = None , cache = False , ignoretz = False , tzinfos = None )
after( self , dt , inc = False )
before( self , dt , inc = False )
between( self , after , before , inc = False , count = 1 )
count( self )
ddayset( self , year , month , day )
exdate( self , exdate )
exrule( self , exrule )
htimeset( self , hour , minute , second )
mdayset( self , year , month , day )
mtimeset( self , hour , minute , second )
rdate( self , rdate )
rebuild( self , year , month )
replace( self , ** kwargs )
rrule( self , rrule )
stimeset( self , hour , minute , second )
wdayset( self , year , month , day )
xafter( self , dt , count = None , inc = False )
ydayset( self , year , month , day )
```

## Module-level constants used by `rrule`

```
FREQNAMES = ['YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY', 'HOURLY', 'MINUTELY', 'SECONDLY']
(YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY) = list(range(7))   # 0 .. 6

class weekday(weekdaybase):        # rrule.weekday; MO, TU, WE, TH, FR, SA, SU = weekday(0) .. weekday(6)
    # attributes: weekday (int, 0 = Monday .. 6 = Sunday), n (int or None; never 0)
    # repr(): 'MO', 'TU', ... when n is None/0, otherwise e.g. 'MO(+1)', 'FR(-2)'
```

## Instance state of `rrule` (set by `rrule.__init__`, read by `__str__`)

| Attribute | Type | Meaning |
|-----------|------|---------|
| `self._dtstart` | `datetime.datetime` | Start of the recurrence, microseconds dropped. Always set by the constructor (defaults to "now"); may be naive or timezone-aware. |
| `self._freq` | `int` 0..6 | Frequency; index into `FREQNAMES`. |
| `self._interval` | `int` >= 1 | Interval between recurrences. |
| `self._wkst` | `int` 0..6 | Week start day (0 = Monday). When not given, `calendar.firstweekday()` (normally 0). |
| `self._count` | `int` or `None` | Maximum number of occurrences. |
| `self._until` | `datetime.datetime` or `None` | Last allowed occurrence. |
| `self._original_rule` | `dict` | The BYxxx rules as the user supplied them (after normalisation), used for string output. Keys (any subset): `'bysetpos'`, `'bymonth'`, `'bymonthday'`, `'byyearday'`, `'byweekno'`, `'byweekday'`, `'byhour'`, `'byminute'`, `'bysecond'`, `'byeaster'`. Values are tuples of `int`, except `'byweekday'`, which is a tuple of `weekday` objects (with `n` set for "nth weekday" rules). A value of `None` marks a rule that was derived automatically from `dtstart` and must not be printed. |

The other `_byxxx` attributes hold the expanded rules used for iteration and are not needed here.
