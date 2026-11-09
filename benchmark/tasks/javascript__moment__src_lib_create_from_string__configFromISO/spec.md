# Functional specification: `configFromISO(config)` in `src/lib/create/from-string.js`

## 1. Component overview

Exported step of moment.js's string parsing. `moment('2013-02-08 09:30')`, `moment.utc(isoString)`
and `moment(str, moment.ISO_8601)` call it to recognise the many ISO 8601 shapes (extended and
basic calendar dates, week dates, ordinal dates, optional time with fractions, optional zone).
It works out the moment format string that describes the input exactly, stores it in `config._f`
and hands over to the format parser; inputs that are not acceptable ISO strings are marked
invalid. It returns nothing; results are written into `config` (see `context.md`).

## 2. Functional requirements

1. **Recognition.** Match `config._i` against `extendedIsoRegex`; if that fails, against
   `basicIsoRegex`. If neither matches, set `config._isValid = false` and stop (the `iso` flag is
   not touched).
2. On a match, set the parsing flag `iso` to `true`.
3. **Date form.** Go through `isoDates` in order and take the first entry whose regular expression
   finds a match inside the date part (capture group 1). Its first element is the date format; the
   date form allows a time unless its third element is `false` (week-only `GGGG-[W]WW`,
   `GGGG[W]WW` and year-month `YYYY-MM`). If no entry matches, set `config._isValid = false` and
   stop.
4. **Time form.** If the time part (group 3) is present and non-empty, take the first `isoTimes`
   entry whose regular expression finds a match inside it; the time format is the separator from
   group 2 (`'T'` or `' '`; a space if group 2 is empty) followed by that entry's format. If no
   entry matches, mark invalid and stop.
5. If the date form does not allow a time but a time format was found, mark invalid and stop.
6. **Zone.** If the zone part (group 4) is present and non-empty: when `tzRegex` finds a match in
   it the zone format is `'Z'`; otherwise mark invalid and stop.
7. Set `config._f` to date format + time format (if any) + zone format (if any), and call
   `configFromStringAndFormat(config)`.

"Mark invalid" always means `config._isValid = false`.

## 3. Input specification

- `config`: a creation config whose `_i` is a string (possibly with leading whitespace, possibly
  not ISO at all), with `_locale`, `_strict`, `_useUTC`/`_isUTC` set; `_f` is undefined or the
  ISO constant and is overwritten on success.

## 4. Output specification

No return value. Resulting `config._f` for some inputs:

- `'2013-02-08'` → `'YYYY-MM-DD'`; `'20130208'` → `'YYYYMMDD'`; `'+002013-02-08'` → `'YYYYYY-MM-DD'`
- `'2013-W06-5'` → `'GGGG-[W]WW-E'`; `'2013W065'` → `'GGGG[W]WWE'`; `'2013-039'` → `'YYYY-DDD'`;
  `'2013050'` → `'YYYYDDD'`; `'2013-02'` → `'YYYY-MM'`
- `'2013-02-08T09'` → `'YYYY-MM-DDTHH'`; `'2013-02-08 09:30:26'` → `'YYYY-MM-DD HH:mm:ss'`
- `'2013-02-08 09:30:26.123'` → `'YYYY-MM-DD HH:mm:ss.SSSS'`; with `,123` → `'… HH:mm:ss,SSSS'`
- `'2013-02-08T09:30:26.123+07:00'` → `'YYYY-MM-DDTHH:mm:ss.SSSSZ'`; `'… 09:30:26 Z'` also ends in `Z`
- `'20130208T080910,123'` → `'YYYYMMDDTHHmmss,SSSS'`; `'20130208T0930'` → `'YYYYMMDDTHHmm'`

Invalid (`_isValid === false`, `_f` unchanged): `'2013-W06T09'` (week date with time),
`'2013-02T09:00'`, `'2013-02-08T9:30'`, `'2013-02-08T0930'` (extended date with basic time), `'2013/02/08'`, `'nope'`, `''`, `'201310'`.
Values out of range (e.g. `'2013-13-01'`) are recognised as ISO here; their invalidity comes from
the format parser.

## 5. Edge cases and constraints

- Order matters: the first matching entry of `isoDates` / `isoTimes` wins.
- Leading whitespace is accepted by the recognisers; trailing text is not.
- The function only writes `config._isValid`, the `iso` flag and `config._f`; everything else is
  done by `configFromStringAndFormat`.
