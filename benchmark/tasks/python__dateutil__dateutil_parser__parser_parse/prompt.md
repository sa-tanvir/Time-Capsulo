You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
## 1. Component overview

The method `parser._parse` (signature in the stub) is the core of
`dateutil.parser.parse`. It turns a free-form date/time string into a `parser._result` record holding the individual fields that
were found (year, month, day, weekday, hour, minute, second, microsecond, time-zone name, time-zone offset, AM/PM flag), plus,
optionally, the pieces of the string that were ignored. It does not build a `datetime`; the public `parse()` does that afterwards
from the record. All vocabulary (month/weekday names, filler words, AM/PM words, UTC names) comes from `self.info`
(a `parserinfo`, see context.md), and numeric tokens are delegated to `self._parse_numeric_token`.

## 2. Functional requirements

1. `fuzzy_with_tokens=True` implies `fuzzy=True`. `dayfirst`/`yearfirst` left as `None` take the values `self.info.dayfirst` /
   `self.info.yearfirst`.
2. Split `timestr` into tokens with `_timelex.split` (a `TypeError` for non-string input such as `None` or `13` must propagate
   unchanged, it is *not* turned into a failed parse). Create a fresh `parser._result()` and a fresh `_ymd()`.
3. Scan the tokens left to right. For the token at position `i`, apply the first matching rule:
   - **Number** (the token is accepted by `float()`, including `"NaN"`/`"inf"`): call
     `_parse_numeric_token` with the token list, the current position, `self.info`, the ymd accumulator, the result and the fuzzy
     flag; continue after the index it returns.
   - **Weekday name**: set `res.weekday` (0 = Monday).
   - **Month name**: add the month number to `ymd`, labelled as the month. If the next token is `-` or `/`, the token after it is
     added to `ymd` too, and if the token two further on is the same separator, the token after that is added as well
     (`"Jan-01-99"`, `"Sep/25/2003"`); all these tokens are consumed. Otherwise, if the following four tokens are
     space, a pertain word (`"of"`), space, X: those four tokens are consumed and, when X consists only of digits, X is the year:
     it is converted with `self.info.convertyear` and added to `ymd` as a labelled year (`"Sep of 03"` gives year 2003 and no
     day; a non-digit X is simply dropped).
   - **AM/PM word**: ask `_ampm_valid` (passing the current hour, the current AM/PM flag and the fuzzy flag). If valid, convert `res.hour` with `self._adjust_ampm` and
     store the flag in `res.ampm`; otherwise, in fuzzy mode, record the token as skipped. (When not fuzzy, an AM/PM word without
     an hour, or with an hour outside 0..12, makes the whole parse fail.)
   - **Time-zone name** (`_could_be_tzname` accepts the token given the current hour, tzname and tzoffset): set `res.tzname` to the token and
     `res.tzoffset` to `self.info.tzoffset(token)`. If the next token is `+` or `-`, that sign token is flipped in the token list
     (POSIX convention: `"GMT+3"` means 3 hours *behind*), `res.tzoffset` is reset to `None`, and if the name was a UTC name the
     tzname is cleared too (`"GMT+3"` is not GMT).
   - **Numeric offset** (`res.hour` already set and the token is `+` or `-`): the next token gives the offset: 4 characters means
     `HHMM`; else if the token after it is `:`, the form is `HH:MM` (consuming the colon and minutes); else 1-2 characters means
     whole hours; anything else fails the parse. `res.tzoffset` = sign x (hours x 3600 + minutes x 60) seconds. If it is then
     followed by a jump token, `(`, a name of at least 3 characters that `_could_be_tzname` accepts (offset ignored for this check),
     and `)`, that name becomes `res.tzname` (`"-0300 (BRST)"`). All consumed tokens are skipped over.
   - **Jump token** (`self.info.jump`), or any token at all in fuzzy mode: record its index as skipped.
   - Otherwise the parse fails.
4. After the scan, resolve the date numbers with the accumulator's `resolve_ymd` (year-first and day-first preferences) and store `res.year`, `res.month`,
   `res.day`, and copy `ymd.century_specified` into the attribute `res.century_specified`.
5. Any `ValueError` or `IndexError` raised during steps 3-4 (by this method or by any helper it calls) makes the method return
   `(None, None)`. Other exceptions propagate.
6. Call `self.info.validate(res)` (it normalises two-digit years and UTC naming in place); if it returns a falsy value return
   `(None, None)`.
7. Return `(res, tuple(self._recombine_skipped(tokens, skipped_indices)))` when `fuzzy_with_tokens` is true, else `(res, None)`.
   The skipped tokens are taken from the (possibly sign-flipped) token list.

## 3. Input specification

- `timestr`: `str`, `bytes`/`bytearray`, or a readable text stream.
- `dayfirst`, `yearfirst`: bool or `None`. `fuzzy`, `fuzzy_with_tokens`: bool.

## 4. Output specification

A 2-tuple. On success: (`parser._result`, `None`) or (`parser._result`, tuple of str) when `fuzzy_with_tokens` is set.
Fields not found stay `None`. On failure: `(None, None)`. Examples (with the default `parserinfo`):
- `"Thu Sep 25 10:36:28 BRST 2003"` -> year 2003, month 9, day 25, weekday 3, hour 10, minute 36, second 28, microsecond 0,
  tzname `"BRST"`, tzoffset None.
- `"2003-09-25T10:49:41.5-03:00"` -> 2003/9/25 10:49:41, microsecond 500000, tzoffset -10800.
- `"1994-11-05T08:15:30Z"` -> tzname `"UTC"`, tzoffset 0 (after validation).
- `"10:49 GMT+3"` -> hour 10, minute 49, tzname None, tzoffset -10800. `"10:49 -0300 (BRST)"` -> tzname `"BRST"`,
  tzoffset -10800.
- `"10:00 pm"` -> hour 22, minute 0, ampm 1. `"12h 01m02s am"` -> hour 0, minute 1, second 2.
- `"Sep of 03"` -> year 2003, month 9, day None.
- `"Today is 25 of September of 2003, exactly at 10:49:41 with timezone -03:00."` with `fuzzy_with_tokens=True` -> 2003/9/25
  10:49:41, tzoffset -10800, skipped `('Today is ', 'of ', ', exactly at ', ' with timezone ', '.')`.
- `"http://biz.yahoo.com/ipo/p/600221.html"` with `fuzzy_with_tokens=True` -> skipped `('http://biz.yahoo.com/ipo/p/', '.html')`.
- `""` -> a result with no fields set (not a failure).
- Failures `(None, None)`: `"shouldfail"`, `"AM"`, `"13:44 AM"`, `"NaN"`, `"1: test"`, `"201A-01-01T23:58"`,
  and, even with `fuzzy_with_tokens=True`, `"04/04/32/423"`, `"04/04/04 +32423"`, `"04/04/0d4"`.

## 5. Edge cases and constraints

- Fuzzy mode never fails just because of an unknown word; it also ignores a second AM/PM word, or an AM/PM word with no valid
  hour (`"I have a meeting on March 1, 1974."` -> 1974/3/1, no hour; `"Meet me at the AM/PM on Sunset at 3:00 AM on December 3rd,
  2003"` -> hour 3). Jump tokens are recorded as skipped in every mode.
- Range errors (e.g. `"2014-15-25"`, `"22:64"`, or `"Jan 20, 2015 PM"`, which yields hour 2015) are not detected here; they surface later when `parse()` builds the datetime.
- Name matching is case-insensitive except the time-zone name rule (upper-case only, or a `parserinfo.UTCZONE` entry).
- Custom `parserinfo` subclasses (other month/weekday names, two-letter weekday names) must work through `self.info`.
- Does not modify `timestr`; each call uses fresh result/ymd objects. Not thread-sensitive beyond `self.info` being read-only.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `dateutil/parser/_parser.py`
- **Enclosing scope:** `class parser(object)`

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
resolve_ymd( self , yearfirst , dayfirst )
split( cls , s )
tzoffset( self , name )
utczone( self , name )
validate( self , res )
weekday( self , name )
```

## Instance state and other members of the enclosing class (you may rely on them)

`parser` has a single instance attribute: `self.info`, a `parserinfo` instance (the default one, or a user subclass).
The nested result class and the helper classes below are defined in the same module and can be used directly.

### `parser._result` (nested class)

A plain record whose `__slots__` are
`["year", "month", "day", "weekday", "hour", "minute", "second", "microsecond", "tzname", "tzoffset", "ampm", "any_unused_tokens"]`.
`parser._result()` builds one with every slot set to `None`. Instances also have a `__dict__`, so extra attributes can be set
(the parse result additionally carries `century_specified`, a bool, which `parserinfo.validate` reads).
`len(res)` is the number of slots that are not `None`; `repr(res)` is `_result(year=2003, month=9, ...)` listing only non-`None` slots.
Meaning of the slots: `year`/`month`/`day`/`hour`/`minute`/`second`/`microsecond` are ints (month 1-12);
`weekday` is an int 0 (Monday) .. 6 (Sunday); `tzname` is a string; `tzoffset` is an int number of seconds east of UTC;
`ampm` is 0 (AM) or 1 (PM) once an AM/PM word has been accepted.

### `parserinfo` (in `self.info`)

Lookup tables are built in `__init__` from the class-level lists (all keys lower-cased):

```
JUMP = [" ", ".", ",", ";", "-", "/", "'", "at", "on", "and", "ad", "m", "t", "of", "st", "nd", "rd", "th"]
WEEKDAYS = [("Mon", "Monday"), ("Tue", "Tuesday"), ("Wed", "Wednesday"), ("Thu", "Thursday"),
            ("Fri", "Friday"), ("Sat", "Saturday"), ("Sun", "Sunday")]
MONTHS = [("Jan", "January"), ("Feb", "February"), ("Mar", "March"), ("Apr", "April"), ("May", "May"),
          ("Jun", "June"), ("Jul", "July"), ("Aug", "August"), ("Sep", "Sept", "September"),
          ("Oct", "October"), ("Nov", "November"), ("Dec", "December")]
HMS = [("h", "hour", "hours"), ("m", "minute", "minutes"), ("s", "second", "seconds")]
AMPM = [("am", "a"), ("pm", "p")]
UTCZONE = ["UTC", "GMT", "Z", "z"]
PERTAIN = ["of"]
TZOFFSET = {}
```

Attributes: `dayfirst` (bool, default False), `yearfirst` (bool, default False), `_year` (current local year), `_century` (`_year // 100 * 100`).
Methods (all name lookups are case-insensitive unless noted):

- `jump(name) -> bool`: True if `name` is a JUMP token (separators/filler such as `" "`, `","`, `"at"`, `"of"`, `"th"`).
- `weekday(name) -> int | None`: 0..6 (Monday=0) for a weekday name/abbreviation, else None.
- `month(name) -> int | None`: 1..12 for a month name/abbreviation, else None.
- `hms(name) -> int | None`: 0 for an hour word (`h`, `hour`, `hours`), 1 for minute words, 2 for second words, else None.
- `ampm(name) -> int | None`: 0 for `am`/`a`, 1 for `pm`/`p`, else None.
- `pertain(name) -> bool`: True for `"of"`.
- `utczone(name) -> bool`: True for UTC/GMT/Z (case-insensitive).
- `tzoffset(name) -> int | None`: 0 if `name` is one of the lower-cased UTC zone keys (`"utc"`, `"gmt"`, `"z"`; this check is case-sensitive), otherwise `TZOFFSET.get(name)` (None by default).
- `convertyear(year, century_specified=False) -> int`: if `year < 100` and the century was not specified, maps the two-digit year into the window [`_year`-50, `_year`+49]; otherwise returns `year` unchanged. Asserts `year >= 0`.
- `validate(res) -> bool`: post-processes a result in place and returns True: converts `res.year` with `convertyear(res.year, res.century_specified)` when the year is set; if (`res.tzoffset == 0` and no tzname) or tzname is `"Z"`/`"z"`, sets tzname `"UTC"` and offset 0; else if the offset is anything other than 0 (None included), a tzname is set and it is a UTC zone name, sets the offset to 0.

### `_ymd` (module-level class, subclass of `list`)

Accumulates up to three date numbers (year/month/day candidates) in order of appearance, as ints.
Attributes: `century_specified` (bool, False initially), `ystridx`, `mstridx`, `dstridx` (index within the list of the value known to be
year / month / day, or None). Properties `has_year`, `has_month`, `has_day` are True when the corresponding index is set.

- `append(val, label=None)`: `val` may be a string of digits, an int, or a `Decimal`. A digit string longer than 2 characters, or a
  number greater than 100, is forced to label `'Y'` and sets `century_specified = True`. The value is stored as `int(val)`
  (so a non-numeric string raises `ValueError` from `int`). Label `'M'`/`'D'`/`'Y'` records the index in `mstridx`/`dstridx`/`ystridx`;
  labelling a second month/day/year raises `ValueError('Month is already set')` / `ValueError('Day is already set')` /
  `ValueError('Year is already set')`.
- `could_be_day(value) -> bool`: False if a day is already known; otherwise whether `1 <= value <=` the length of the known month
  (31 if no month known; leap-year February if the month is known but the year is not).
- `resolve_ymd(yearfirst, dayfirst) -> (year, month, day)`: decides which collected value is year, month and day (any may be None),
  using the labelled indices, value ranges (e.g. > 31 must be a year) and the `dayfirst`/`yearfirst` preferences.
  Raises `ValueError("More than three YMD values")` if more than three values were collected and they are not all labelled.
  It never converts two-digit years (that is done later by `parserinfo.validate`).

### `_timelex.split(s) -> list[str]` (module-level class, classmethod)

Tokenizer. Accepts `str`, `bytes`/`bytearray` (decoded) or any object with a `read` method; anything else raises
`TypeError('Parser must be a string or character stream, not <type>')`. NUL characters are ignored. Produces maximal runs of
letters, maximal runs of digits (a number may contain one decimal point or a comma used as decimal separator, which is normalised
to `.`), each whitespace character as a single `" "` token, and every other character as its own one-character token.
Dot-separated mixtures are split at the dots, keeping the dots as tokens. Examples:
`"2003-09-25T10:49:41.5-03:00"` -> `['2003', '-', '09', '-', '25', 'T', '10', ':', '49', ':', '41.5', '-', '03', ':', '00']`;
`"Sep.20.2009"` -> `['Sep', '.', '20', '.', '2009']`; `"10:49:41,502"` -> `[..., '41.502']`; `"10am"` -> `['10', 'am']`;
`"5:50 A.M."` -> `['5', ':', '50', ' ', 'A', '.', 'M', '.']`.

### Sibling methods of `parser` (all available on `self`)

- `_to_decimal(val) -> Decimal`: `Decimal(val)`; raises `ValueError("Could not convert %s to decimal" % val)` (chained) if the
  conversion fails or the result is infinite/NaN.
- `_parsems(value: str) -> (int, int)`: seconds string `"I"` or `"I.F"` -> `(seconds, microseconds)`, fraction truncated/padded to
  6 digits; `"41.5"` -> `(41, 500000)`, `"01.123456789"` -> `(1, 123456)`.
- `_parse_min_sec(value: Decimal) -> (int, int | None)`: `(int(value), int(60 * fractional part))`, the second item None when there
  is no fractional part. `Decimal("36.5")` -> `(36, 30)`.
- `_find_hms_idx(idx, tokens, info, allow_jump) -> int | None`: index of the h/m/s label that applies to the numeric token at
  `idx`: the next token if it is an hms word; else (if `allow_jump`) the token after a single `" "` if that is an hms word; else
  the previous token if it is an hms word; else, when `idx` is the last token, the token two back if separated by `" "` and it is an
  hms word; else None.
- `_parse_hms(idx, tokens, info, hms_idx) -> (new_idx, hms)`: turns that label index into `(index of last consumed token, field)`:
  for a following label, `(hms_idx, info.hms(label))`; for a preceding label the field is the *next* one (`info.hms(label) + 1`,
  e.g. the `04` in `12h04` is minutes) and the index is unchanged; for None, `(idx, None)`.
- `_assign_hms(res, value_repr, hms)`: stores the numeric string into `res` as hour (0; a fractional hour also sets minutes, e.g.
  `"4.2"` -> hour 4 minute 12), minute (1; fractional part gives seconds) or second (2; fractional part gives microseconds).
- `_ampm_valid(hour, ampm, fuzzy) -> bool`: whether an AM/PM word should be applied. Not fuzzy: raises
  `ValueError('No hour specified with AM or PM flag.')` when hour is None and
  `ValueError('Invalid hour specified for 12-hour clock.')` when hour is outside 0..12, otherwise True.
  Fuzzy: returns False instead of raising in those cases, and also False when an AM/PM flag was already set.
- `_adjust_ampm(hour, ampm) -> int`: converts a 12-hour clock hour: adds 12 for PM when hour < 12; maps 12 AM to 0.
- `_could_be_tzname(hour, tzname, tzoffset, token) -> bool`: True when an hour has been parsed, no tzname and no tzoffset are set
  yet, and `token` is at most 5 characters long and is either all ASCII upper-case letters or one of `parserinfo.UTCZONE`.
- `_recombine_skipped(tokens, skipped_idxs) -> list[str]`: joins the tokens at the given (sorted) indices into strings, merging
  runs of consecutive indices: tokens `["foo", " ", "bar", " ", "19June2000", "baz"]`, indices `[0, 1, 2, 5]` -> `["foo bar", "baz"]`.
- `parse(timestr, default=None, ignoretz=False, tzinfos=None, **kwargs)`: public entry point; calls
  `self._parse(timestr, **kwargs)`, raises `ParserError("Unknown string format: %s", timestr)` if it returns `(None, None)` and
  `ParserError("String does not contain a date: %s", timestr)` if the result has no fields set, then builds the datetime from the
  result (missing fields from `default`) and attaches tz info. With `fuzzy_with_tokens=True` it returns `(datetime, skipped_tokens)`.
- `_parse_numeric_token(tokens, idx, info, ymd, res, fuzzy) -> int`: interprets the numeric token `tokens[idx]` (one that
  `float()` accepts) together with any following tokens it needs (`:`-separated times, `-`/`/`/`.`-separated dates, h/m/s labels,
  a following AM/PM word, compact forms such as `20030925`, `104941`, `199709020908`), appending date numbers to `ymd` and setting
  time fields on `res`. Returns the index of the *last* token it consumed (so scanning continues at the returned value + 1).
  Raises `ValueError` (e.g. `'Unknown numeric token'` for `"NaN"`/`"inf"`, an uninterpretable number when not fuzzy, or an error
  from `_ymd.append`) and may raise `IndexError` for truncated input such as `"01-01-"`. When `fuzzy` is True an uninterpretable
  number is silently ignored instead of raising.

=== STUB ===
```python
def _parse(self, timestr, dayfirst=None, yearfirst=None, fuzzy=False,
           fuzzy_with_tokens=False):
    raise NotImplementedError  # TODO: implement according to the specification
```
