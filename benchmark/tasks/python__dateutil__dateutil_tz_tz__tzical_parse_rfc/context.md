# Context for the function to implement

- **Language:** python
- **File:** `dateutil/tz/tz.py`
- **Enclosing scope:** `class tzical(object)`

## Imports / includes available in this file

```
import datetime
import struct
import time
import sys
import os
import bisect
import weakref
from collections import OrderedDict
import six
from six import string_types
from six.moves import _thread
from ._common import tzname_in_python2, _tzinfo
from ._common import tzrangebase, enfold
from ._common import _validate_fromutc_inputs
from ._factories import _TzSingleton, _TzOffsetFactory
from ._factories import _TzStrFactory
from warnings import warn
```

## Other functions defined in the same file (signatures only; you may call them)

```
__get_gettz( )
__get_gettz.cache_clear( self )
__get_gettz.nocache( name = None )
__get_gettz.set_cache_size( self , size )
_datetime_to_timestamp( dt )
_delta( self , x , isend = 0 )
_dst_base_offset( self )
_find_comp( self , dt )
_find_compdt( self , comp , dt )
_find_last_transition( self , dt , in_utc = False )
_find_ttinfo( self , dt )
_get_supported_offset( second_offset )
_get_ttinfo( self , idx )
_isdst( self , dt , fold_naive = True )
_naive_is_dst( self , dt )
_parse_offset( self , s )
_read_tzfile( self , fileobj )
_resolve_ambiguous_time( self , dt )
_set_tzdata( self , tzobj )
datetime_ambiguous( dt , tz = None )
datetime_exists( dt , tz = None )
dst( self , dt )
fromutc( self , dt )
get( self , tzid = None )
is_ambiguous( self , dt )
is_ambiguous( self , dt , idx = None )
keys( self )
resolve_imaginary( dt )
transitions( self , year )
tzname( self , dt )
utcoffset( self , dt )
```

## Instance state and other members of the enclosing class (you may rely on them)

```
class tzical(object):
    def __init__(self, fileobj):
        global rrule
        from dateutil import rrule      # the module dateutil.rrule is bound to the module-level
                                        # global name `rrule` before _parse_rfc is called
        self._s = ...                   # file name / repr, only used by __repr__
        self._vtz = {}                  # dict: TZID (str) -> _tzicalvtz; filled by _parse_rfc
        with fileobj as fobj:
            self._parse_rfc(fobj.read())   # the whole text is passed to the method to implement

    def keys(self):                     # list(self._vtz.keys())
    def get(self, tzid=None):           # self._vtz.get(tzid); with tzid None, the single zone
                                        # (ValueError if there are 0 or more than 1 zones)

    def _parse_offset(self, s):
        """Parses a UTC offset string into an int number of seconds.
        Surrounding whitespace is stripped; an optional leading '+' or '-' gives the sign
        (default '+'); the rest must be 'HHMM' or 'HHMMSS'.
        '-0500' -> -18000, '+0130' -> 5400, '0100' -> 3600, '+013015' -> 5415.
        Raises ValueError('empty offset') for an empty string and
        ValueError('invalid offset: ' + digits) for any other length (digits = the part after the sign)."""
```

Helper classes defined in the same module (constructors you can call):

```
class _tzicalvtzcomp(object):
    """One STANDARD or DAYLIGHT sub-component of a VTIMEZONE."""
    def __init__(self, tzoffsetfrom, tzoffsetto, isdst, tzname=None, rrule=None):
        # tzoffsetfrom / tzoffsetto: int seconds (stored as datetime.timedelta)
        # isdst: bool (True for DAYLIGHT components)
        # tzname: str or None
        # rrule: an object from dateutil.rrule (rrule/rruleset) giving the onset date-times, or None

class _tzicalvtz(_tzinfo):
    """A tzinfo built from one VTIMEZONE."""
    def __init__(self, tzid, comps=[]):   # tzid: str; comps: list of _tzicalvtzcomp (kept in the given order)
```

Function available from `dateutil.rrule` (via the global `rrule`):
`rrule.rrulestr(s, dtstart=None, cache=False, unfold=False, forceset=False, compatible=False,
ignoretz=False, tzids=None, tzinfos=None)` parses newline-separated iCalendar recurrence lines
(`DTSTART`, `RRULE`, `RDATE`, `EXRULE`, `EXDATE`) and returns an `rrule` or `rruleset`;
with `compatible=True` it always returns an `rruleset` that also includes DTSTART as an occurrence.
It raises `ValueError` for malformed recurrence lines.
