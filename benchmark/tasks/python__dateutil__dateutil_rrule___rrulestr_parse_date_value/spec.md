# Functional specification

## 1. Component overview

`_rrulestr._parse_date_value` converts the value of an iCalendar (RFC 5545) `DTSTART` or `EXDATE` content line into a list of `datetime.datetime` objects. It is called by `_rrulestr._parse_rfc` (the engine of the public `dateutil.rrule.rrulestr`) after the line has been upper-cased and split into a property name, a list of parameters and a value. Example line: `EXDATE;VALUE=DATE-TIME;TZID=Europe/Brussels:19970902T090000,19970909T090000` arrives here as `date_value="19970902T090000,19970909T090000"`, `parms=["VALUE=DATE-TIME", "TZID=EUROPE/BRUSSELS"]`.

## 2. Functional requirements

**Parameters** (`parms`, processed in order, before any date is parsed):
- `TZID=<NAME>`: `<NAME>` (the text after `TZID=`) is looked up in `rule_tzids`, a dict mapping upper-cased TZID names to their original spelling. If it is not a key there, the parameter is silently ignored. Otherwise the original spelling is resolved to a `tzinfo` through `tzids`:
  - `tzids is None`: use `dateutil.tz.gettz(original_name)`;
  - `tzids` callable: call `tzids(original_name)` (exceptions it raises propagate unchanged);
  - otherwise `tzids` must have a `get` method (a mapping): use `tzids.get(original_name)` (missing key gives `None`, i.e. no zone);
  - anything else (no `get`, not callable) -> `ValueError("tzids must be a callable, mapping, or None, not %s" % tzids)`, e.g. `tzids=42` -> message ending in `not 42`.
  The resolved zone (possibly `None`) becomes the zone to attach; a later TZID parameter overrides an earlier one.
- `VALUE=DATE-TIME` or `VALUE=DATE`: accepted, but only once in total: a second `VALUE=...` parameter -> `ValueError("Duplicate value parameter found in: " + parm)` (e.g. `"... in: VALUE=DATE"`). The VALUE kind does not change how dates are parsed.
- Any other parameter -> `ValueError("unsupported parm: " + parm)` (e.g. `"unsupported parm: VALUE=PERIOD"`).

**Values.** `date_value` is split on `,`; each piece is parsed with `dateutil.parser.parse(piece, ignoretz=ignoretz, tzinfos=tzinfos)`. If a zone was resolved from TZID (not `None`):
- a naive parsed datetime gets that zone attached (wall time unchanged, no conversion);
- an already aware parsed datetime (e.g. `"19970902T090000Z"`, or an explicit offset) -> `ValueError('DTSTART/EXDATE specifies multiple timezone')`.
With no resolved zone, parsed datetimes are returned as the parser produced them.

Examples (with `tzids={'Eastern': EST}`, `rule_tzids={'EASTERN': 'Eastern'}`):
- `("19970902T090000", [], ...)` -> `[datetime(1997, 9, 2, 9, 0)]`
- `("19970902", ["VALUE=DATE"], ...)` -> `[datetime(1997, 9, 2, 0, 0)]`
- `("19970904T090000,19970911T090000", [], ...)` -> two datetimes, in input order
- `("19970902T090000", ["TZID=EASTERN"], ...)` -> `[datetime(1997, 9, 2, 9, 0, tzinfo=EST)]`
- `("19970902T090000Z", ["TZID=EASTERN"], ...)` -> `ValueError`
- `("19970902T090000", ["TZID=OTHER"], ...)` (OTHER not in `rule_tzids`) -> naive result.

## 3. Input specification

- `date_value`: `str`, one or more date or date-time strings separated by commas, in any format `dateutil.parser.parse` accepts (typically `YYYYMMDD` or `YYYYMMDDTHHMMSS`, optionally with `Z`).
- `parms`: list of `str` parameters (already upper-case), possibly empty.
- `rule_tzids`: `dict` from upper-case TZID name to original-case name.
- `ignoretz`: `bool`, forwarded to the parser (zone information in the strings is dropped; TZID zones are still attached).
- `tzids`: `None`, a callable `name -> tzinfo`, or a mapping (anything with `.get`).
- `tzinfos`: forwarded to `dateutil.parser.parse` (mapping/callable of zone names), may be `None`.

## 4. Output specification

A new `list` of `datetime.datetime`, one per comma-separated piece, in input order. Inputs are not modified. The `dateutil.parser` module is imported lazily on first use (see the module-level `parser` placeholder in the context).

## 5. Edge cases and constraints

- All parameter validation happens before any value is parsed, so an unsupported parameter is reported even if the dates are invalid.
- A TZID whose name is not in `rule_tzids` is skipped without consulting `tzids`, so a bad `tzids` value only raises when a lookup is actually needed.
- Unparsable pieces (including an empty piece produced by a trailing comma) raise whatever `dateutil.parser.parse` raises (a `ValueError` subclass, e.g. `ParserError("Unknown string format: %s", ...)`).
- The multiple-timezone check applies only when a non-`None` zone was resolved; a TZID that resolves to `None` (missing mapping key) leaves aware values untouched.
- Errors raised by a user `tzids` callable are not wrapped.
- No state is kept between calls.
