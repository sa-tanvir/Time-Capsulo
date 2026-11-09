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

`isoparser._parse_isotime(timestr)` parses the time-of-day portion of an ISO-8601 string into a list of components. It is the shared back end of `isoparser.parse_isotime` (which turns the list into a `datetime.time`) and of `isoparser.isoparse` (which calls it with everything after the date/time separator and appends the components to the date). Both public wrappers convert `str` input to ASCII `bytes` first, so `timestr` is always a `bytes` object here.

## 2. Functional requirements

The accepted grammar is: `hh`, `hhmm` / `hh:mm`, `hhmmss` / `hh:mm:ss`, each optionally followed — only after the seconds — by a fractional part, and then optionally by a time-zone designator.

1. **Hour, minute, second**: each is exactly two characters converted with `int`. Whether colons are used is decided by the third byte only: if the string is at least 3 bytes long and its third byte is `:` (the class constant `_TIME_SEP`), a single `:` is skipped after the hour and after the minute when present. Without a colon at position 2, the components must be contiguous digits. Missing trailing components default to 0.
2. **Fraction of a second**: after the seconds, a `.` or `,` followed by one or more ASCII digits (the class regex `_FRACTION_REGEX`). Only the first 6 digits are used (extra digits are truncated, never rounded); fewer digits are right-padded, i.e. scaled to microseconds: `.5` → 500000, `.123` → 123000, `.123456999999` → 123456.
3. **Time zone**: as soon as the next unread byte (at any component boundary) is one of `-`, `+`, `Z`, `z`, the entire remainder of the string is parsed with `self._parse_tzstr(remainder)` (default `zero_as_utc=True`), and parsing stops. Its result (`tz.UTC` / a `tz.tzoffset`) becomes the fifth component. Errors raised by `_parse_tzstr` propagate unchanged, e.g. `ValueError('Time zone offset must be 1, 3, 5 or 6 characters')` for `+`, `ValueError('Invalid hours in time zone offset')` for `+25:00`, `ValueError('Invalid minutes in time zone offset')` for `+12:62`, `ValueError('Time zone offset requires sign')`.
4. **Leftovers**: if anything remains unconsumed after hour, minute, second, fraction and time zone, raise `ValueError('Unused components in ISO string')` (e.g. `14:30:15.`, `14:30:15:16`, `14:30:15.1.2`).
5. **Midnight as 24**: an hour of 24 is only allowed if minute, second and microsecond are all 0; otherwise raise `ValueError('Hour may only be 24 at 24:00:00.000')`. When allowed, 24 is returned as-is (callers map it to midnight of the next day / 00:00).
6. No other range checks: values such as hour 25 or minute 61 are returned unchanged (the caller's `datetime`/`time` constructor rejects them).

## 3. Input specification

- `timestr`: `bytes`, ASCII, the time part only (no leading date or `T`). Examples: `b'14'`, `b'1430'`, `b'14:30:15.224+05:00'`.

## 4. Output specification

A new `list` of exactly five items `[hour, minute, second, microsecond, tzinfo]`: four `int`s and `tzinfo` which is `None` when no zone designator was present.

Examples:
- `b'14'` → `[14, 0, 0, 0, None]`; `b'1430'` and `b'14:30'` → `[14, 30, 0, 0, None]`
- `b'143015'` / `b'14:30:15'` → `[14, 30, 15, 0, None]`
- `b'143015,123456789'` → `[14, 30, 15, 123456, None]`
- `b'14:30:15Z'` → `[14, 30, 15, 0, tzutc()]`; `b'14z'` → `[14, 0, 0, 0, tzutc()]`
- `b'14+05'` → `[14, 0, 0, 0, tzoffset(None, 18000)]`
- `b'14:30-0530'` → `[14, 30, 0, 0, tzoffset(None, -19800)]`
- `b'14:30:15.123+00:00'` → `[14, 30, 15, 123000, tzutc()]`
- `b'24'`, `b'24:00'`, `b'24:00:00.000'` → `[24, 0, 0, 0, None]`
- `b'24:01'`, `b'24:00:01'`, `b'24:00:00.000001'` → `ValueError('Hour may only be 24 at 24:00:00.000')`
- `b'25:61:99'` → `[25, 61, 99, 0, None]`

## 5. Edge cases and constraints

- Input shorter than 2 bytes (including empty) → `ValueError('ISO time too short')`.
- Non-digit two-character components raise the `ValueError` produced by `int()` (e.g. `b'14_30'`, `b'1430:15'` — inconsistent separators).
- A fraction is only recognised after the seconds component.
- A string that would need more than hour, minute, second, fraction and zone is rejected with the "Unused components" error, e.g. `b'14:30:15.34468305:00'` (zone without sign) and `b'14:59:30_344583'` (bad fraction separator).
- The 24-hour check happens after the whole string was parsed successfully.
- Pure function of `timestr` and the class constants; it does not modify instance state.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `dateutil/parser/isoparser.py`
- **Enclosing scope:** `class isoparser(object)`

## Imports / includes available in this file

```
from datetime import datetime, timedelta, time, date
import calendar
from dateutil import tz
from functools import wraps
import re
import six
```

## Other functions defined in the same file (signatures only; you may call them)

```
_calculate_weekdate( self , year , week , day )
_parse_isodate( self , dt_str )
_parse_isodate_common( self , dt_str )
_parse_isodate_uncommon( self , dt_str )
_parse_tzstr( self , tzstr , zero_as_utc = True )
_takes_ascii( f )
_takes_ascii.func( self , str_in , * args , ** kwargs )
isoparse( self , dt_str )
parse_isodate( self , datestr )
parse_isotime( self , timestr )
parse_tzstr( self , tzstr , zero_as_utc = True )
```

## Instance state and other members of the enclosing class (you may rely on them)

The public entry points are decorated with `_takes_ascii`, which reads streams and encodes `str`
input to ASCII `bytes` (raising `ValueError` for non-ASCII). Therefore `_parse_isotime` always
receives `bytes`. Callers: `parse_isotime(timestr)` returns `time(*components)` (mapping hour 24
to 0); `isoparse(dt_str)` calls `self._parse_isotime(dt_str[pos + 1:])` for the part after the
date/time separator.

Class-level constants:

```
class isoparser(object):
    _DATE_SEP = b'-'
    _TIME_SEP = b':'
    _FRACTION_REGEX = re.compile(b'[\\.,]([0-9]+)')
```

Instance attribute: `self._sep` (the configured date/time separator as bytes, or `None`); not
relevant for the time portion.

`_parse_tzstr(self, tzstr, zero_as_utc=True)`: parses a bytes time-zone designator. `b'Z'`/`b'z'`
→ `tz.UTC`. Otherwise the length must be 3, 5 or 6 (`ValueError('Time zone offset must be 1, 3,
5 or 6 characters')`), the first byte must be `+` or `-` (`ValueError('Time zone offset requires
sign')`), and forms `±HH`, `±HHMM`, `±HH:MM` are accepted. A zero offset gives `tz.UTC` when
`zero_as_utc`; otherwise minutes > 59 → `ValueError('Invalid minutes in time zone offset')`,
hours > 23 → `ValueError('Invalid hours in time zone offset')`, else
`tz.tzoffset(None, sign * (hours * 60 + minutes) * 60)`.

=== STUB ===
```python
def _parse_isotime(self, timestr):
    raise NotImplementedError  # TODO: implement according to the specification
```
