# Functional specification: `localeWeekdaysParse(weekdayName, format, strict)` in `src/lib/units/day-of-week.js`

## 1. Component overview

Exported function installed as the `Locale` method `weekdaysParse`. moment.js calls it while
parsing a date string with weekday tokens (`dddd` full name, `ddd` short name, `dd` min name), and
when a weekday is set by name (`m.day('Monday')`, `m.isoWeekday('Sunday')`, the latter without
format/strict). It converts a weekday name written in the locale's language into the weekday
index `0` (Sunday) … `6` (Saturday). `this` is the `Locale` (see "Instance state" in
`context.md`).

## 2. Functional requirements

1. **Exact mode.** If the locale's `_weekdaysParseExact` flag is truthy, return the result of
   `handleStrictParse` (called with the same `this` and arguments) and do nothing else.
2. **Pattern mode** (otherwise). For each weekday `i` from 0 to 6, in that order, using the
   locale's names of weekday `i` (via `this.weekdays/weekdaysShort/weekdaysMin` with a moment
   whose weekday is `i` and an empty format string):
   - **Strict** (`strict` truthy): the full, short and min names are each turned into a
     case-insensitive regular expression that must match the **whole** input: the name text is
     used as a regular-expression source (it is *not* escaped), except that the **first** `.`
     in each name is made a literal, optional period (so `'dim.'` accepts `'dim.'` and `'dim'`,
     and `'t...s'` does not match `'thurs'`). With `format` `'dddd'` the full-name pattern is
     tested, with `'ddd'` the short-name pattern, with `'dd'` the min-name pattern; any other
     format never matches in strict mode.
   - **Lenient** (`strict` falsy): one case-insensitive pattern per weekday that matches when the
     input **starts with** the full name, the short name or the min name (in that order of
     alternatives). It is built from the three names as regular-expression sources joined as
     alternatives, after which the **first `.` of that whole combined pattern** is removed (any
     later `.` keeps its regular-expression meaning). The format is ignored.
   - Return `i` for the first weekday whose applicable pattern matches.
3. If no weekday matches, return `undefined` (the function simply ends without a value).
4. **Caching.** The patterns are built lazily and stored per weekday in the locale's cache arrays
   (`_weekdaysParse` for lenient patterns; `_fullWeekdaysParse`, `_shortWeekdaysParse`,
   `_minWeekdaysParse` for strict ones), creating the arrays on first use. An entry that already
   exists is reused, not rebuilt. The lenient pattern for a weekday is built when it is first
   reached even during a strict call; the strict patterns only during strict calls.

## 3. Input specification

- `weekdayName`: string to parse (may be empty, contain trailing text, any case).
- `format`: the moment format token (`'dddd'`, `'ddd'`, `'dd'`), another string, or `undefined`.
- `strict`: boolean or `undefined`.
- `this`: a `Locale`; its weekday names are strings (possibly with periods), its first day of the
  week does not matter here.

## 4. Output specification

A weekday index `0`–`6`; otherwise `undefined` in pattern mode, `null` in exact mode. Examples
with the default English locale (`Sunday…Saturday`, `Sun…Sat`, `Su…Sa`):

- `('Monday', 'dddd', true)` → `1`; `('monday', 'dddd', true)` → `1`
- `('Mon', 'dddd', true)` → `undefined`; `('Mon', 'ddd', true)` → `1`; `('Mo', 'dd', true)` → `1`
- `('Mon', 'd', true)` → `undefined`
- `('Monday')` → `1`; `('Mozart', 'dd', false)` → `1` (prefix match); `('Sunday!', 'dddd', false)` → `0`
- `('Sunday!', 'dddd', true)` → `undefined`; `('Thursday', 'ddd', false)` → `4`; `('xyz', 'dddd', false)` → `undefined`

French-like locale (`dimanche…`, short `dim. lun. …`, min `Di Lu …`):

- `('lun.', 'ddd', true)` → `1`; `('lun', 'ddd', true)` → `1`; `('lunx', 'ddd', true)` → `undefined`
- `('lu', 'ddd', false)` → `1`; `('Ma', 'dd', true)` → `2`

Locale with weekdays `Monday, T....day, Wednesday, Thursday, …` and short names
`mon, t...s, wed, thurs, …` (non-exact): `moment('thurs', 'ddd', true)` resolves to Thursday,
i.e. `('thurs', 'ddd', true)` returns Thursday's index, because `t...s` does not match `thurs`.

## 5. Edge cases and constraints

- Matching is case-insensitive; the input is not trimmed.
- Weekdays are tried from 0 upwards, so with ambiguous lenient patterns the lowest index wins.
- The only side effect is filling the caches on `this`; arguments are not modified.
- Independent of time zone and current time.
