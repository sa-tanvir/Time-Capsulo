# Context for the function to implement

- **Language:** python
- **File:** `dateutil/parser/_parser.py`
- **Enclosing scope:** `class _ymd(list)`

## Imports / includes available in this file

```
from __future__ import unicode_literals
import datetime
import re
import string
import time
import warnings
from calendar import monthrange
from io import StringIO
import six
from six import integer_types, text_type
from decimal import Decimal
from warnings import warn
from .. import relativedelta
from .. import tz
```

## Other functions defined in the same file (signatures only; you may call them)

```
_adjust_ampm( self , hour , ampm )
_ampm_valid( self , hour , ampm , fuzzy )
_assign_hms( self , res , value_repr , hms )
_assign_tzname( self , dt , tzname )
_build_naive( self , res , default )
_build_tzaware( self , naive , res , tzinfos )
_build_tzinfo( self , tzinfos , tzname , tzoffset )
_convert( self , lst )
_could_be_tzname( self , hour , tzname , tzoffset , token )
_find_hms_idx( self , idx , tokens , info , allow_jump )
_parse( self , timestr , dayfirst = None , yearfirst = None , fuzzy = False , fuzzy_with_tokens = False )
_parse_hms( self , idx , tokens , info , hms_idx )
_parse_min_sec( self , value )
_parse_numeric_token( self , tokens , idx , info , ymd , res , fuzzy )
_parsems( self , value )
_parsetz( tzstr )
_recombine_skipped( self , tokens , skipped_idxs )
_repr( self , classname )
_resolve_from_stridxs( self , strids )
_to_decimal( self , val )
ampm( self , name )
append( self , val , label = None )
convertyear( self , year , century_specified = False )
could_be_day( self , value )
get_token( self )
has_day( self )
has_month( self )
has_year( self )
hms( self , name )
isnum( cls , nextchar )
isspace( cls , nextchar )
isword( cls , nextchar )
jump( self , name )
month( self , name )
next( self )
parse( self , timestr , default = None , ignoretz = False , tzinfos = None , ** kwargs )
parse( self , tzstr )
parse( timestr , parserinfo = None , ** kwargs )
pertain( self , name )
split( cls , s )
tzoffset( self , name )
utczone( self , name )
validate( self , res )
weekday( self , name )
```

## Instance state and other members of the enclosing class (you may rely on them)

```
class _ymd(list):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.century_specified = False
        self.dstridx = None   # index of the entry known to be the day, or None
        self.mstridx = None   # index of the entry known to be the month, or None
        self.ystridx = None   # index of the entry known to be the year, or None

    @property
    def has_year(self):  return self.ystridx is not None
    @property
    def has_month(self): return self.mstridx is not None
    @property
    def has_day(self):   return self.dstridx is not None
```

`append(val, label=None)` stores `int(val)`; a digit string longer than 2 characters or a number
greater than 100 is automatically labelled `'Y'` (and sets `century_specified`). Label `'M'`, `'D'`
or `'Y'` records the new entry's index in `mstridx`, `dstridx` or `ystridx` respectively (raising
`ValueError` if that label is already set).

`_resolve_from_stridxs(self, strids)`: `strids` is a dict mapping some of the keys `'y'`, `'m'`,
`'d'` to list indices. Must be called only when `len(self) == len(strids)`, or when
`len(self) == 3 and len(strids) == 2` (it then fills in the missing key with the unused index;
it mutates the passed dict). Returns `(year, month, day)` read from those indices, with `None`
for keys absent from `strids`.
