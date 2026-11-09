# Functional specification: `localeMonthsParse(monthName, format, strict)` in `src/lib/units/month.js`

## 1. Component overview

Exported function installed as the `Locale` method `monthsParse`. moment.js calls it when parsing
the month-name tokens `MMMM` (long name) and `MMM` (short name) — the token is passed as `format`,
the parser's strictness as `strict` — and when a month is set by name (`m.month('March')`,
without format/strict). It converts a month name in the locale's language into the month index
`0` (January) … `11` (December). If the parser gets no index back it marks the date invalid
(`invalidMonth` parsing flag). `this` is the `Locale` (see "Instance state" in `context.md`).

## 2. Functional requirements

1. **Exact mode.** If the locale's `_monthsParseExact` flag is truthy, return the result of
   `handleStrictParse` (same `this` and arguments) and do nothing else.
2. **Pattern mode** (otherwise). For each month `i` from 0 to 11, in order, with the locale's long
   and short names of month `i` (via `this.months` / `this.monthsShort` with a moment in month `i`
   and an empty format string):
   - **Strict** (`strict` truthy): a case-insensitive pattern for the long name and one for the
     short name, each required to match the **whole** input. The name text is used as a
     regular-expression source (not escaped), except that its **first `.` is removed**
     (so short name `janv.` accepts `janv` but not `janv.`). With `format === 'MMMM'` the long-name
     pattern is tested, with `'MMM'` the short-name pattern; any other format never matches.
   - **Lenient** (`strict` falsy): one case-insensitive pattern per month matching when the input
     **starts with** the long name or the short name (long name first). It is built from both
     names as regular-expression sources joined as alternatives, after which the **first `.` of
     that combined pattern** is removed (later periods keep their regular-expression meaning). The
     format is ignored.
   - Return `i` for the first month whose applicable pattern matches.
3. If no month matches, return `undefined`.
4. **Caching / presets.** Patterns live in the per-month cache arrays (`_monthsParse` for lenient,
   `_longMonthsParse` / `_shortMonthsParse` for strict). Create the three arrays (as empty arrays)
   if `_monthsParse` does not exist yet. If an entry already exists — built by an earlier call or
   supplied by the locale config — use it as is (a strict call checks the long-name entry: if it
   is missing, both the long and the short pattern of that month are (re)built). Lenient patterns
   are only built during lenient calls, strict ones only during strict calls.

## 3. Input specification

- `monthName`: the string to parse (any case, may have trailing text, may be empty).
- `format`: `'MMMM'`, `'MMM'`, another string, or `undefined`.
- `strict`: boolean or `undefined`.
- `this`: a `Locale` with 12 long and 12 short month names (strings, possibly with periods,
  possibly with separate format/standalone forms), optionally with preset pattern arrays.

## 4. Output specification

A month index `0`–`11`; otherwise `undefined` in pattern mode (`null` in exact mode). Examples
with the default English locale:

- `('March', 'MMMM', true)` → `2`; `('march', 'MMMM', true)` → `2`; `('Mar', 'MMMM', true)` → `undefined`
- `('Mar', 'MMM', true)` → `2`; `('March', 'MMM', true)` → `undefined`; `('Mar', 'M', true)` → `undefined`
- `('Marchxx', 'MMM', false)` → `2`; `('Sept', 'MMM', false)` → `8`; `('May')` → `4`; `('Ma')` → `undefined`
- `('xyz', 'MMM', false)` → `undefined`

French-like locale (long `janvier…`, short `janv. févr. mars avr. mai juin juil. …`):

- `('janv', 'MMM', true)` → `0`; `('janv.', 'MMM', true)` → `undefined`; `('juil.', 'MMM', true)` → `undefined`
- `('janvx', 'MMM', false)` → `0`; `('juin', 'MMMM', false)` → `5`

A locale whose config supplies `monthsParse`/`longMonthsParse`/`shortMonthsParse` arrays such as
`[/^янв/i, /^фев/i, …, /^ма[йя]/i, …]` uses exactly those patterns: `('мая', 'MMMM', true)` → `4`.
Locale with names `one…twelve` for both long and short: `('seven', 'MMM')` → `6`.

## 5. Edge cases and constraints

- Matching is case-insensitive; the input is not trimmed.
- Months are tried from 0 upwards, so for ambiguous lenient patterns the lowest index wins.
- Side effects are limited to filling the caches on `this`; arguments are not modified.
- Independent of time zone and current time.
