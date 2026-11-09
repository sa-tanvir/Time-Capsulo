# Context for the function to implement

- **Language:** python
- **File:** `dateutil/rrule.py`
- **Enclosing scope:** `class _rrulestr(object)`

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

## Instance state and other members of the enclosing class (you may rely on them)

`_rrulestr` is a stateless parser class; the module creates one instance, `rrulestr = _rrulestr()`,
whose `__call__(self, s, **kwargs)` simply returns `self._parse_rfc(s, **kwargs)`.

Module-level names you may use (all defined in `dateutil/rrule.py`):

```
# Imported on demand (lazy import to avoid a circular import).
parser = None          # module global; becomes the dateutil.parser module once imported:
                       #     global parser
                       #     if not parser:
                       #         from dateutil import parser
YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY = range(7)
MO, TU, WE, TH, FR, SA, SU = weekdays   # weekday instances
class rrule(rrulebase):    rrule(freq, dtstart=None, interval=1, wkst=None, count=None, until=None,
                                 bysetpos=None, bymonth=None, bymonthday=None, byyearday=None,
                                 byeaster=None, byweekno=None, byweekday=None, byhour=None,
                                 byminute=None, bysecond=None, cache=False)
class rruleset(rrulebase): rruleset(cache=False) with methods
                           .rrule(r)  .rdate(dt)  .exrule(r)  .exdate(dt)  (each appends to the set)
```

Class constants and sibling methods of `_rrulestr`:

```
_freq_map = {"YEARLY": YEARLY, "MONTHLY": MONTHLY, "WEEKLY": WEEKLY, "DAILY": DAILY,
             "HOURLY": HOURLY, "MINUTELY": MINUTELY, "SECONDLY": SECONDLY}
_weekday_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
```

- `_handle_<NAME>(self, rrkwargs, name, value, **kwargs)` - one handler per RRULE part name
  (FREQ, INTERVAL, COUNT, UNTIL, WKST, BYSETPOS, BYMONTH, BYMONTHDAY, BYYEARDAY, BYEASTER,
  BYWEEKNO, BYHOUR, BYMINUTE, BYSECOND, BYDAY/BYWEEKDAY); each stores the converted value into
  the `rrkwargs` dict. UNTIL values are parsed with `dateutil.parser.parse` (honouring the
  `ignoretz` / `tzinfos` keyword arguments). Used only by `_parse_rfc_rrule`.
- `_parse_rfc_rrule(self, line, dtstart=None, cache=False, ignoretz=False, tzinfos=None)` ->
  `rrule`. `line` is either `"RRULE:<parts>"` or just `"<parts>"` (upper-case,
  `NAME=VALUE` pairs separated by `;`). Raises `ValueError("unknown parameter name")` if the
  prefix before `:` is not `RRULE`, `ValueError("unknown parameter '<NAME>'")` for an unknown
  part name, and `ValueError("invalid '<NAME>': <VALUE>")` when a part value cannot be
  converted. Returns `rrule(dtstart=dtstart, cache=cache, **parts)`; the `rrule` constructor
  may itself raise `ValueError` (e.g. `"RRULE UNTIL values must be specified in UTC when
  DTSTART is timezone-aware"`).
- `_parse_date_value(self, date_value, parms, rule_tzids, ignoretz, tzids, tzinfos)` -> `list`
  of `datetime`. Converts a DTSTART/EXDATE value: `date_value` is a comma-separated list of
  date(-time) strings, `parms` the list of property parameters (e.g. `["VALUE=DATE"]`,
  `["TZID=EASTERN"]`, upper-case), `rule_tzids` a dict mapping upper-cased TZID names to their
  original spelling. Applies the TZID time zone (looked up through `tzids`: mapping, callable,
  or `dateutil.tz.gettz` when `None`) to naive results. Raises `ValueError` for unsupported
  parameters (`"unsupported parm: ..."`), a duplicated `VALUE=` parameter, a TZID combined
  with an already-aware date (`"DTSTART/EXDATE specifies multiple timezone"`), or a `tzids`
  of the wrong type; exceptions from a `tzids` callable propagate. Imports `dateutil.parser`
  lazily itself.
