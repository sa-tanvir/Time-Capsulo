You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification

## 1. Component overview

`_ymd.resolve_ymd(yearfirst, dayfirst)` is the final step of dateutil's free-form date parser. While a date string is tokenised, every number (or month name) that could be part of the date is appended to a `_ymd` object, which is a `list` of up to three integers. Some entries carry a *label* recorded by `append` (see context.md): the position of an entry known to be a month (`mstridx`, e.g. it came from a month name such as "Sep"), a year (`ystridx`, e.g. it had more than two digits or was greater than 100) or a day (`dstridx`). `resolve_ymd` decides which entry is the year, which is the month and which is the day, using the labels, the magnitudes of the values, and the two ambiguity hints `yearfirst` and `dayfirst`. It does not validate ranges (e.g. month 13 can be returned) and must not modify the object.

## 2. Functional requirements

Let *n* be the number of entries and *L* the set of labels that are present.

**A. Fully determined by labels.** If *n* ≥ 1 and every entry is labelled (*n* equals the number of labels), or *n* = 3 and exactly two entries are labelled (the unlabelled entry then takes the one remaining role), the result is read directly from the labelled positions; roles that do not occur are `None`. This uses the sibling `_resolve_from_stridxs` (context.md).

**B. More than three entries** (when rule A does not apply): raise `ValueError("More than three YMD values")`.

**C. One entry**, or **two entries one of which is the month label** (and rule A did not apply): the month-labelled entry (if any) is the month; the remaining entry is the year if it is greater than 31, otherwise the day.

**D. Two unlabelled-as-month entries** `[a, b]` (any year/day label is ignored here):
- a > 31: year = a, month = b ("99-01")
- else b > 31: month = a, year = b ("01-99")
- else `dayfirst` and b ≤ 12: day = a, month = b ("13-01" style)
- otherwise month = a, day = b.

**E. Three entries `[a, b, c]` with the month label at position**
- 0: if b > 31 → month a, year b, day c ("Apr-2003-25"); else month a, day b, year c.
- 1: if a > 31, or (`yearfirst` and c ≤ 31) → year a, month b, day c; otherwise day a, month b, year c ("01-Jan-01" defaults to day-first).
- 2: if b > 31 → day a, year b, month c; else year a, day b, month c.

**F. Three entries without a month label** (a single year or day label may exist):
- If a > 31, or the year label is at position 0, or (`yearfirst` and b ≤ 12 and c ≤ 31): the year is a; then if `dayfirst` and c ≤ 12 the order is year, day, month, otherwise year, month, day.
- Else if a > 12, or (`dayfirst` and b ≤ 12): day a, month b, year c.
- Otherwise: month a, day b, year c.
A day label, or a year label at position 1 or 2, does not influence rule F.

**G. No entries**: `(None, None, None)`.

## 3. Input specification

- `self`: a `_ymd` instance (list of 0..n Python `int`s, normally positive; years may be 2-digit or 4-digit) with attributes `ystridx`, `mstridx`, `dstridx` each `None` or a valid index into the list (distinct from each other).
- `yearfirst`, `dayfirst`: truthy/falsy values (normally `bool`).

## 4. Output specification

A 3-tuple `(year, month, day)`; each element is one of the list's integers or `None` if that role is not present. Year values are returned as stored (no century conversion is done here).

Examples (labels shown as `M`, `Y`):
- `[2003(Y), 9(M), 25]` → `(2003, 9, 25)` (rule A)
- `[2015(Y), 15, 5(M)]` → `(2015, 5, 15)` (rule A, "2015-15-May")
- `[10, 9, 3]`, yearfirst=False, dayfirst=False → `(3, 10, 9)`; dayfirst=True → `(3, 9, 10)`; yearfirst=True → `(10, 9, 3)`; both True → `(10, 3, 9)`
- `[13, 9, 3]` → `(3, 9, 13)`
- `[99, 1, 2]` → `(99, 1, 2)`; with dayfirst=True → `(99, 2, 1)`
- `[9(M), 25]` → `(None, 9, 25)`; `[9(M), 45]` → `(45, 9, None)`
- `[12]` → `(None, None, 12)`; `[45]` → `(45, None, None)`
- `[3, 25]` → `(None, 3, 25)`; `[13, 1]` with dayfirst=True → `(None, 1, 13)`; `[99, 1]` → `(99, 1, None)`
- `[1(M), 99, 25]` → `(99, 1, 25)`
- four entries → `ValueError("More than three YMD values")`

## 5. Edge cases and constraints

- Comparisons are strict: 31 counts as a possible day, 32 is a year; 12 counts as a possible month.
- The method is pure: it must not change the list contents or the label attributes.
- No range validation and no exceptions other than the "more than three" `ValueError`.
- Through `parser.parse` this determines results such as "Sep 03 10" vs. dayfirst/yearfirst variants and "2015-15-May"; a `ValueError` here makes the parse fail.

=== CONTEXT ===
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

=== STUB ===
```python
def resolve_ymd(self, yearfirst, dayfirst):
    raise NotImplementedError  # TODO: implement according to the specification
```
