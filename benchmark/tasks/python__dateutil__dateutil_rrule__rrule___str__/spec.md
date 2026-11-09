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
