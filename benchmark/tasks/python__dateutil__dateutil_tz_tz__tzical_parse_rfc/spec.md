# Functional specification: `tzical._parse_rfc(self, s)`

## 1. Component overview

`tzical` reads iCalendar (RFC 5545 section 3.6.5) `VTIMEZONE` definitions and turns each of them
into a `tzinfo` object. `_parse_rfc` receives the complete text of the iCalendar data and fills
`self._vtz`, mapping every successfully closed `VTIMEZONE`'s `TZID` to a `_tzicalvtz` built from
its `STANDARD` / `DAYLIGHT` sub-components (`_tzicalvtzcomp` objects). It returns `None`. Invalid
or unsupported content raises `ValueError`.

Example input (CRLF or LF line endings are both accepted):

```
BEGIN:VTIMEZONE
TZID:US-Eastern
LAST-MODIFIED:19870101T000000Z
TZURL:http://zones.stds_r_us.net/tz/US-Eastern
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
END:DAYLIGHT
END:VTIMEZONE
```

yields `self._vtz == {'US-Eastern': <tzicalvtz 'US-Eastern'>}` whose components are, in order,
(from -4h, to -5h, isdst False, name 'EST') and (from -5h, to -4h, isdst True, name 'EDT'). A
datetime of 2003-07-01 12:00 in that zone then reports `EDT` / -4h, and 2003-01-15 12:00 reports
`EST` / -5h.

## 2. Functional requirements

1. **Lines.** Split `s` into lines (any line-break convention, as `str.splitlines`). If there are
   no lines at all (e.g. `s == ""`), raise `ValueError("empty string")`.
2. **Unfolding and cleaning.** Strip trailing whitespace from every line and discard lines that
   become empty. A line that begins with a single space and is not the first remaining line is a
   continuation: it is appended, without that leading space, to the preceding remaining line
   (several continuation lines may follow each other). Only a leading space (not a tab) marks a
   continuation.
3. **Content lines.** Each remaining line has the form `NAME[;PARAM...]:VALUE`, split at the first
   `':'` (the value may contain further colons). The part before the colon is split on `';'`: the
   first element, upper-cased, is the property name; the others are the parameters (kept as is).
   The value is used exactly as written (not stripped, not case-converted).
4. **Outside a VTIMEZONE** every line is ignored, except `BEGIN:VTIMEZONE` (value compared
   case-sensitively), which opens a new time-zone block with no TZID and no components yet.
5. **Inside a VTIMEZONE, outside a sub-component:**
   - `TZID`: sets the zone id to the value; with parameters, raise
     `ValueError("unsupported TZID parm: " + first_param)`.
   - `TZURL`, `LAST-MODIFIED`, `COMMENT`: ignored.
   - `BEGIN` with value `STANDARD` or `DAYLIGHT`: opens a sub-component of that type; any other
     value raises `ValueError("unknown component: " + value)`.
   - `END:VTIMEZONE` closes the zone: if no TZID was given (missing or empty) raise
     `ValueError("mandatory TZID not found")`; if it has no components raise
     `ValueError("at least one component is needed")`; otherwise store a
     `_tzicalvtz` built from the TZID and the component list under key TZID in `self._vtz` (components in input order; a later zone
     with the same TZID replaces the earlier one) and return to the outside state.
   - `END` with any other value: `ValueError("invalid component end: " + value)`.
   - Any other property: `ValueError("unsupported property: " + NAME)` (upper-cased name).
6. **Inside a STANDARD/DAYLIGHT sub-component:**
   - `DTSTART`: the only accepted parameter is `VALUE=DATE-TIME`; any other parameter raises
     `ValueError("Unsupported DTSTART param in VTIMEZONE: " + param)`. The line counts as the
     component's start.
   - `DTSTART`, `RRULE`, `RDATE`, `EXRULE`, `EXDATE` lines are collected, in order and as complete
     (unfolded) lines, as the component's recurrence description.
   - `TZOFFSETFROM` / `TZOFFSETTO`: value parsed with `self._parse_offset` (seconds). With
     parameters raise `ValueError("unsupported TZOFFSETFROM parm: " + param + " ")` (note the
     trailing space) or `ValueError("unsupported TZOFFSETTO parm: " + param)` respectively.
   - `TZNAME`: the component's name; with parameters raise
     `ValueError("unsupported TZNAME parm: " + param)`.
   - `COMMENT`: ignored.
   - `BEGIN:STANDARD` / `BEGIN:DAYLIGHT`: abandons the unfinished component and starts a new one of
     the given type (other `BEGIN` values: `ValueError("unknown component: " + value)`).
   - `END:VTIMEZONE`: `ValueError("component not closed: " + TYPE)` (TYPE = `STANDARD`/`DAYLIGHT`).
   - `END` whose value equals the open component type closes it:
     - no DTSTART seen: `ValueError("mandatory DTSTART not found")`;
     - no TZOFFSETFROM: `ValueError("mandatory TZOFFSETFROM not found")`;
     - no TZOFFSETTO: `ValueError("mandatory TZOFFSETFROM not found")` (the same message, as in the
       original library);
     - otherwise the collected recurrence lines, joined with `"\n"`, are parsed with
       `rrule.rrulestr` with the options compatible, ignoretz and cache all enabled and the component
       `_tzicalvtzcomp(offset_from, offset_to, type == "DAYLIGHT", tzname_or_None, recurrence)` is
       appended to the zone's components. Errors from `rrulestr` / `_parse_offset` propagate.
   - `END` with another value: `ValueError("invalid component end: " + value)`.
   - Any other property: `ValueError("unsupported property: " + NAME)`.
7. If the input ends while a `VTIMEZONE` is still open, that zone is silently discarded; zones
   closed earlier remain stored. Any number of `VTIMEZONE` blocks may appear, possibly surrounded
   by other iCalendar content (e.g. `BEGIN:VCALENDAR`, `PRODID:...`), which is ignored.

## 3. Input specification

- `s`: `str`, the full iCalendar text.
- `self`: a `tzical` whose `_vtz` is a (normally empty) dict; the module global `rrule` refers to
  `dateutil.rrule` (see context).

## 4. Output specification

- Returns `None`. Effect: entries added to (or replaced in) `self._vtz`.
- A `ValueError` aborts parsing; zones stored before the error stay in `self._vtz`.

## 5. Edge cases and constraints

- `""` raises `ValueError("empty string")`; a text containing only whitespace lines or no
  `VTIMEZONE` at all is accepted and adds nothing.
- Property names are case-insensitive (`tzname:EST` works); `BEGIN`/`END` values and
  `VALUE=DATE-TIME` are case-sensitive.
- A `DTSTART;VALUE=DATE:...` or `DTSTART;TZID=UTC:...` inside a component raises the
  "Unsupported DTSTART param" error.
- A non-empty line without any `':'` raises `ValueError` (message unspecified).
- Offsets such as `+013015` (with seconds) are allowed.
- Must not consult the system time-zone database or the clock.
