You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `rrule.__str__(self)`

## 1. Component overview

`rrule.__str__` serialises a recurrence rule (`dateutil.rrule.rrule`) into
iCalendar (RFC 5545) text: a `DTSTART` line followed by an `RRULE` line.
Passing the result to `dateutil.rrule.rrulestr` must produce a rule that
generates exactly the same occurrences as the original. The output is mostly
RFC 5545 compatible, plus dateutil's own `BYEASTER` extension. The instance
attributes it reads and the module constants are documented in `context.md`.

## 2. Functional requirements

1. **DTSTART line.** If a start datetime is set (`self._dtstart` truthy), the
   first line is `DTSTART:` followed by the start formatted as
   `YYYYMMDDTHHMMSS` (4-digit year, 2-digit month/day/hour/minute/second, a
   literal `T`), e.g. `DTSTART:19970902T090000`. No time-zone suffix or `Z`
   is written, even for timezone-aware datetimes.
2. **RRULE line.** The last line is `RRULE:` followed by `;`-separated
   `NAME=value` parts, in exactly this order:
   1. `FREQ=<name>`: always present; the name is `FREQNAMES[self._freq]`
      (`YEARLY`, `MONTHLY`, `WEEKLY`, `DAILY`, `HOURLY`, `MINUTELY`,
      `SECONDLY`).
   2. `INTERVAL=<n>`: only if the interval is not 1.
   3. `WKST=<day>`: only if the week start is not Monday (i.e. `self._wkst`
      is non-zero); `<day>` is the two-letter code `MO TU WE TH FR SA SU`
      for 0..6.
   4. `COUNT=<n>`: whenever `self._count` is not `None` (also for 0).
   5. `UNTIL=<YYYYMMDDTHHMMSS>`: only if `self._until` is set, same format as
      DTSTART, no zone suffix.
   6. The BYxxx parts, taken from `self._original_rule`, in this fixed order:
      `BYSETPOS` (key `bysetpos`), `BYMONTH` (`bymonth`), `BYMONTHDAY`
      (`bymonthday`), `BYYEARDAY` (`byyearday`), `BYWEEKNO` (`byweekno`),
      `BYDAY` (`byweekday`), `BYHOUR` (`byhour`), `BYMINUTE` (`byminute`),
      `BYSECOND` (`bysecond`), `BYEASTER` (`byeaster`). A part is written only
      if its key is present with a non-empty value (missing keys, `None` and
      empty tuples are skipped). The value is the elements in their stored
      order, each converted with `str`, joined by `,` (no spaces), e.g.
      `BYMONTHDAY=1,3,-1`. (The constructor already stores multi-valued BY
      parameters as sorted tuples, so the stored order is ascending; e.g.
      `byeaster=(0, 1, -1)` is stored as `(-1, 0, 1)`.)
   7. `BYDAY` elements are weekday objects and are written as RFC 5545 day
      codes: a plain weekday is its two-letter code (`MO`), an "nth weekday"
      is the signed ordinal followed by the code, with an explicit sign:
      `+1MO`, `-1FR`, `+20TU`.
3. If both lines are present they are joined with a single `\n`; there is no
   trailing newline.
4. The rule object must not be modified (in particular
   `self._original_rule` keeps its weekday objects), so repeated calls give
   identical strings.

Examples:

- `rrule(YEARLY, count=5, dtstart=datetime(1997, 9, 2, 9, 0))` gives
  `'DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=5'` (the month/day
  derived from dtstart are not printed).
- `str(rrulestr('DTSTART:19970105T083000\nRRULE:FREQ=YEARLY;INTERVAL=2'))`
  returns the same text.
- `rrule(MONTHLY, count=3, byweekday=(TU(1), TH(-1)), dtstart=datetime(1997, 9, 2, 9, 0))`
  gives `'DTSTART:19970902T090000\nRRULE:FREQ=MONTHLY;COUNT=3;BYDAY=+1TU,-1TH'`.
- `rrule(WEEKLY, interval=2, wkst=SU, byweekday=(TU, SU), until=datetime(1998, 1, 1), dtstart=datetime(1997, 8, 5, 9, 0))`
  gives `'DTSTART:19970805T090000\nRRULE:FREQ=WEEKLY;INTERVAL=2;WKST=SU;UNTIL=19980101T000000;BYDAY=TU,SU'`.
- `rrule(DAILY, count=2, bysetpos=(1, -1), bymonth=(1, 3), byhour=(6, 18), byminute=(0, 30), bysecond=(15,), dtstart=datetime(1997, 9, 2, 9, 0))`
  gives `'DTSTART:19970902T090000\nRRULE:FREQ=DAILY;COUNT=2;BYSETPOS=1,-1;BYMONTH=1,3;BYHOUR=6,18;BYMINUTE=0,30;BYSECOND=15'`.
- `rrule(YEARLY, count=3, byeaster=(0, 1, -1), dtstart=datetime(1997, 9, 2, 9, 0))`
  gives `'DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3;BYEASTER=-1,0,1'`.

## 3. Input specification

`self` is a fully constructed `rrule`. Relevant state (see `context.md`):
`_dtstart` (datetime), `_freq` (int 0..6), `_interval` (int >= 1), `_wkst`
(int 0..6), `_count` (int or None), `_until` (datetime or None) and
`_original_rule` (dict of BYxxx key to tuple or `None`).

## 4. Output specification

A `str` of one or two lines as described above. Integers are written in plain
decimal with a leading `-` for negatives (no `+`), except the `BYDAY`
ordinals, which always carry a sign.

## 5. Edge cases and constraints

- Rules that were derived automatically (stored as `None` in
  `_original_rule`) are omitted, e.g. a plain `WEEKLY` rule has no `BYDAY`.
- `wkst=MO` (or the default) never produces a `WKST` part.
- `COUNT` and `UNTIL` may both appear (in that order).
- Timezone information of `dtstart`/`until` is not represented.
- No I/O; does not mutate the rule; safe to call repeatedly.

=== CONTEXT ===
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

=== STUB ===
```python
def __str__(self):
    raise NotImplementedError  # TODO: implement according to the specification
```
