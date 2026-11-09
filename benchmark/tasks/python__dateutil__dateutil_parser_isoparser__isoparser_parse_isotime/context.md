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
