# Functional specification: `isValidDate(str)` in `src/lib/isISO8601.js`

## 1. Component overview

Module-private helper (an arrow function bound to the constant `isValidDate`) of the
validator.js ISO 8601 validator. `isISO8601(str, options)` first checks the syntax of `str`
against the `iso8601` pattern; when `options.strict` is truthy and the syntax is valid, it
returns `isValidDate(str)`, which rejects dates that are syntactically fine but do not exist on
the calendar, such as `2009-02-29` or day 366 of a common year.

## 2. Functional requirements

1. **Ordinal dates.** If the string starts with a 4-digit year, an optional `-`, and exactly 3
   digits (the day of the year), followed either by the end of the string or by a space or `T`
   (anything may follow that), it is an ordinal date. Return `true` if the day number is at most
   366 in a leap year, or at most 365 otherwise; else `false`. Leap years are those divisible by
   4 but not by 100, plus those divisible by 400 (Gregorian rule). The number 000 is not
   rejected by this helper.
2. **All other forms.** Take the first run of 4 digits in the string as the year, then (after an
   optional `-`) up to 2 digits as the month, then (after an optional `-`) all directly following
   digits as the day. A missing month or day counts as 0.
   - If both month and day are non-zero, return `true` only if the month is 1–12 and that day
     exists in that month of that year in the proleptic Gregorian calendar (e.g. February has
     29 days in leap years, April/June/September/November have 30); otherwise `false` (a month
     above 12, or a day above the month's length, e.g. a 3-digit day, gives `false`).
   - If the month or the day is missing/zero (year only, year-month, week dates like
     `2009-W21-2`, which yield no month digits), return `true`, whatever the other number is
     (even a month above 12).
3. Any time, fraction or time-zone part after the date is ignored. A leading `+` or `-` sign of
   the year is not part of the year (`'-2008-02-29'` is checked as 2008-02-29, `'+2009-02-29'`
   is `false`). Because rule 1 requires the 4 year digits at the very start of the string, a
   **signed ordinal date is not recognised as ordinal** and is read by rule 2 instead: its 3
   digits split into a 2-digit month and a 1-digit day. So `'+2009-123'` is checked as
   2009-12-03 (`true`), `'-2008-366'` as month 36, day 6 (`false`), `'+2009-310'` as month 31,
   day 0 (`true`), and `'+2009-001'` as month 0 (`true`).

## 3. Input specification

- `str`: a string that already matches the module's `iso8601` pattern (calendar dates
  `YYYY-MM-DD`/`YYYYMMDD`, `YYYY-MM`, `YYYY`, ordinal dates `YYYY-DDD`/`YYYYDDD`, week dates
  `YYYY-Www-D`/`YYYYWwwD`, each optionally followed by a time and zone, optionally with a sign
  before the year). Years are in the range 1000–9999. Other strings never reach this function.

## 4. Output specification

A boolean. Examples:

- `true`: `'2000-02-29'`, `'20000229'`, `'2009-05-19'`, `'2009-05-19T14:39:22-06:00'`,
  `'2009-123'`, `'2009-222'`, `'2009365'`, `'2020-366'`, `'2400-366'`, `'2000-366'`,
  `'2008366'`, `'2009'`, `'2009-05'`, `'2009-W01-1'`, `'2009W511'`, `'2009-12T12:34'`,
  `'2007-04-05T24:00'`, `'2009-123 10'`
- `false`: `'2010-02-30'`, `'2009-02-29'`, `'20090229'`, `'2009-02-29T10:00Z'`, `'2019-02-31'`,
  `'2009-04-31'`, `'2009-366'`, `'2009366'`, `'2100-366'`, `'1900-366'`, `'+2009-02-29'`

## 5. Edge cases and constraints

- Day 366 is valid exactly in leap years (2000 and 2400 are leap years, 1900 and 2100 are not).
- The ordinal rule takes precedence: `'2009-123T10:00'` is an ordinal date (day 123), not a
  month/day date.
- The time part is not validated here (e.g. hour `24:00` is accepted).
- Pure function: no side effects, does not depend on the local time zone.
