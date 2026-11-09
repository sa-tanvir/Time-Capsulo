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

## Instance state and other members of the enclosing class (you may rely on them)

`_rrulestr` is a stateless parser class (no instance attributes); the module creates one
instance, `rrulestr = _rrulestr()`, whose `__call__` forwards to `_parse_rfc`. `_parse_rfc`
calls this method for every `DTSTART` and `EXDATE` line, passing the upper-cased value, the
upper-cased parameter list, a dict `{UPPER_TZID_NAME: OriginalTzidName}` collected from the
original text, and its own `ignoretz`, `tzids`, `tzinfos` arguments unchanged.

Module-level names in `dateutil/rrule.py` relevant here:

```
# Imported on demand (lazy import to avoid a circular import).
parser = None          # module global; becomes the dateutil.parser module once imported:
                       #     global parser
                       #     if not parser:
                       #         from dateutil import parser
```

`dateutil.tz` is NOT imported at module level; import it locally when needed
(`from . import tz`, then `tz.gettz(name)` returns a `tzinfo` or `None`).

`dateutil.parser.parse(timestr, ignoretz=False, tzinfos=None)` returns a `datetime.datetime`
(naive unless the string carries zone information and `ignoretz` is false) and raises a
`ValueError` subclass (`ParserError`) for unparsable input.

Other class constants (not needed here): `_freq_map` (frequency name -> `YEARLY`..`SECONDLY`),
`_weekday_map` (`"MO"`..`"SU"` -> 0..6), and the `_handle_<NAME>` / `_parse_rfc_rrule` helpers
that turn an RRULE text into an `rrule`.
