You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isISO8601.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
```

## Other functions defined in the same file (signatures only; you may call them)

```
isISO8601 ( str , options )
```

## Variables declared at the same scope level (you may use them)

```
const iso8601 = /^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-3])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$/;
```

=== STUB ===
```javascript
const isValidDate = (str) => {
    // TODO: implement according to the specification
}
```
