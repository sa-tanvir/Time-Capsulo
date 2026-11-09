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

`_rrulestr._parse_rfc` is the engine behind the public `dateutil.rrule.rrulestr(s, **kwargs)` callable (the module-level `rrulestr` object is an `_rrulestr` instance whose `__call__` forwards to this method). It parses an iCalendar (RFC 5545) style recurrence description - one or more content lines such as `DTSTART`, `RRULE`, `RDATE`, `EXRULE`, `EXDATE` - and returns either a single `rrule` or an `rruleset` object. It is the inverse of `str(rrule)`: for any rule `r`, `list(rrulestr(str(r))) == list(r)`, and e.g. `str(rrulestr("DTSTART:19970105T083000\nRRULE:FREQ=YEARLY;INTERVAL=2"))` gives back exactly that text.

## 2. Functional requirements

**Option handling.** `compatible=True` implies both `forceset=True` and `unfold=True`.

**Case.** Parsing is case-insensitive: the whole text is upper-cased before it is interpreted (`"dtstart:19970902T090000\nrrule:freq=yearly;count=3"` behaves like the upper-case version). The only exception is time-zone identifiers: the original spelling of every `TZID=<name>:` occurrence in the *original* text is remembered (name = everything after `TZID=` up to the next `:`), and lookups are done with that original spelling, so `tzids={'Eastern': tz}` works for `DTSTART;TZID=Eastern:...`.

**Splitting into lines.**
- Without `unfold`, the text is split on any whitespace (spaces, newlines), so `" DTSTART:19970902T090000  RRULE:FREQ=YEARLY;COUNT=3 "` is two lines.
- With `unfold`, the text is split into physical lines; trailing whitespace is removed from each; empty lines are dropped; a line beginning with a single space is a continuation and is appended (minus that first space) to the preceding line. Example: `"FREQ=YEA\n RLY;COUNT=3\n"` with `unfold=True` is the single line `FREQ=YEARLY;COUNT=3`.

**Single-rule shortcut.** If `forceset` is false, there is exactly one line, and the (upper-cased) text either contains no `:` at all or begins with `RRULE:`, the result is the rule obtained by passing that line to `self._parse_rfc_rrule` with the given `dtstart`, `cache`, `ignoretz` and `tzinfos`. Examples: `"FREQ=YEARLY;COUNT=3"` or `"RRULE:FREQ=YEARLY;COUNT=3"` with `dtstart=datetime(1997,9,2,9,0)` yield 1997-09-02 09:00, 1998-09-02 09:00, 1999-09-02 09:00.

**General case.** Otherwise each non-empty line is processed in order:
- A line without `:` is treated as an `RRULE` value. Otherwise the part before the first `:` is the property name, optionally followed by `;`-separated parameters; the part after is the value.
- `RRULE`: any parameter -> `ValueError("unsupported RRULE parm: <parm>")`. The value is kept for later.
- `RDATE`: any parameter other than `VALUE=DATE-TIME` -> `ValueError("unsupported RDATE parm: <parm>")`. The value is kept for later.
- `EXRULE`: any parameter -> `ValueError("unsupported EXRULE parm: <parm>")`. The value is kept for later.
- `EXDATE`: value and parameters are converted immediately with `self._parse_date_value(value, parms, <TZID name map>, ignoretz, tzids, tzinfos)`; all returned datetimes are collected.
- `DTSTART`: converted the same way; if the conversion does not give exactly one datetime -> `ValueError("Multiple DTSTART values specified:" + value)` (no space after the colon). The single datetime replaces the `dtstart` argument (the last `DTSTART` line wins).
- Any other name -> `ValueError("unsupported property: <NAME>")`.

The `<TZID name map>` maps each upper-cased TZID name to its original spelling.

After all lines are read, a **set** is built when `forceset` is true, or there is more than one rule line, or there is at least one RDATE, EXRULE or EXDATE: a new `rruleset(cache=cache)` receives, in this order, every RRULE (parsed with `self._parse_rfc_rrule(value, dtstart=<final dtstart>, ignoretz=..., tzinfos=...)`, i.e. not cached), every RDATE item (each RDATE value is split on `,` and each piece parsed with `dateutil.parser.parse(piece, ignoretz=ignoretz, tzinfos=tzinfos)`), every EXRULE (parsed like RRULEs), and every collected EXDATE datetime. When `compatible` is true and a `dtstart` (argument or DTSTART line) is known, that datetime is additionally added as an rdate. Otherwise the single RRULE value is parsed with `self._parse_rfc_rrule` using the final `dtstart`, `cache`, `ignoretz`, `tzinfos` and returned.

Example: `"DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=6;BYDAY=TU,TH\nEXDATE:19970904T090000,19970911T090000,19970918T090000"` gives an `rruleset` yielding 1997-09-02, 09-09, 09-16 (all 09:00). `"DTSTART:19970902T090000\nRRULE:FREQ=YEARLY;COUNT=3"` gives an `rrule`, but with `forceset=True` an `rruleset`.

## 3. Input specification

- `s`: `str`, the recurrence text.
- `dtstart`: `datetime` or `None`, default start used when no DTSTART line is present.
- `cache`: `bool`, forwarded to the returned object's constructor.
- `unfold`, `forceset`, `compatible`, `ignoretz`: `bool` flags described above (`ignoretz` makes the date parser drop zone information).
- `tzids`: `None`, a callable, or a mapping from TZID name to `tzinfo`; only forwarded to the date-value conversion (with `None`, `dateutil.tz.gettz` is used there).
- `tzinfos`: forwarded to `dateutil.parser.parse` (mapping or callable of zone names/aliases).

## 4. Output specification

Returns a `dateutil.rrule.rrule` or `dateutil.rrule.rruleset` as described. Nothing is iterated; errors raised while building rules (`rrule` constructor checks, e.g. a naive UNTIL with an aware DTSTART raising `ValueError`) propagate directly from this call.

## 5. Edge cases and constraints

- A text that is empty or only whitespace -> `ValueError("empty string")`.
- Errors from rule parsing propagate unchanged, e.g. `"invalid 'BYDAY': -1OK"`, `"invalid 'FREQ': FORTNIGHTLY"`, `"unknown parameter 'FOO'"`, `"invalid 'UNTIL': ..."` (all `ValueError`).
- Errors from date-value conversion propagate, e.g. a TZID combined with a `Z`-suffixed date (`ValueError`), unsupported/duplicate `VALUE=` parameters, or any exception raised by a user `tzids` callable (not wrapped).
- Unparsable RDATE pieces raise whatever `dateutil.parser.parse` raises (a `ValueError` subclass).
- When there are no rule lines, no dates and `forceset` is false (e.g. a lone `DTSTART` line), there is no rule to return; this input is unsupported (an `IndexError` results).
- DTSTART may appear anywhere among the lines; it applies to all RRULE/EXRULE lines, because rules are created only after all lines are read.
- The `dateutil.parser` module is imported lazily the first time it is needed (see the module-level `parser` placeholder in the context).
- The function does not mutate its arguments and keeps no state between calls.

=== CONTEXT ===
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

=== STUB ===
```python
def _parse_rfc(self, s,
               dtstart=None,
               cache=False,
               unfold=False,
               forceset=False,
               compatible=False,
               ignoretz=False,
               tzids=None,
               tzinfos=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
