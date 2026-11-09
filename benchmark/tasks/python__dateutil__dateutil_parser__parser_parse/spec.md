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
