You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/units/month.js`

## Imports / includes available in this file

```
import { get } from '../moment/get-set';
import hasOwnProp from '../utils/has-own-prop';
import { addFormatToken } from '../format/format';
import { addUnitAlias } from './aliases';
import { addUnitPriority } from './priorities';
import { addRegexToken, match1to2, match2, matchWord, regexEscape } from '../parse/regex';
import { addParseToken } from '../parse/token';
import { hooks } from '../utils/hooks';
import { MONTH } from './constants';
import toInt from '../utils/to-int';
import isArray from '../utils/is-array';
import isNumber from '../utils/is-number';
import mod from '../utils/mod';
import indexOf from '../utils/index-of';
import { createUTC } from '../create/utc';
import getParsingFlags from '../create/parsing-flags';
import { isLeapYear } from '../units/year';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( )
(anonymous) ( format )
(anonymous) ( input , array )
(anonymous) ( input , array , config , token )
(anonymous) ( isStrict , locale )
cmpLenRev ( a , b )
computeMonthsParse ( )
daysInMonth ( year , month )
getDaysInMonth ( )
getSetMonth ( value )
handleStrictParse ( monthName , format , strict )
localeMonths ( m , format )
localeMonthsShort ( m , format )
monthsRegex ( isStrict )
monthsShortRegex ( isStrict )
setMonth ( mom , value )
```

## Variables declared at the same scope level (you may use them)

```
var MONTHS_IN_FORMAT = /D[oD]?(\[[^\[\]]*\]|\s)+MMMM?/;
var defaultMonthsShortRegex = matchWord;
var defaultMonthsRegex = matchWord;
```

## Instance state (`this` is a `Locale` object; the function is installed as `Locale.prototype.monthsParse`)

Attributes read or written:

| attribute | type | meaning |
|---|---|---|
| `this._monthsParseExact` | boolean or undefined | locale config flag `monthsParseExact`; when truthy, parsing is exact (string comparison) and handled by `handleStrictParse` |
| `this._monthsParse` | array (indices 0–11) or undefined | per-month cache of the lenient pattern (`RegExp`) for month `i`; may be pre-populated by the locale config (`monthsParse: [/^янв/i, …]`), otherwise filled lazily; created as `[]` on first use |
| `this._longMonthsParse` | array or undefined | per-month cache of the strict long-name pattern; may be pre-populated by the config (`longMonthsParse`) |
| `this._shortMonthsParse` | array or undefined | per-month cache of the strict short-name pattern; may be pre-populated by the config (`shortMonthsParse`) |

A locale whose config pre-populates `monthsParse` also pre-populates `longMonthsParse` and
`shortMonthsParse`. (`handleStrictParse` stores lower-cased strings in `_longMonthsParse` /
`_shortMonthsParse` instead; a locale uses one mode or the other, never both.)

Sibling methods / helpers used:

- `this.months(m, format)`, `this.monthsShort(m, format)`: given a moment `m`, return the
  locale's long / short name of `m`'s month (for an empty format string the "standalone" form is
  used when the locale distinguishes forms).
- `createUTC([2000, i])` (imported from `../create/utc`): a UTC moment for the first day of month
  `i` (0 = January … 11 = December) of the year 2000.
- `handleStrictParse(monthName, format, strict)` (same file; call it with
  `handleStrictParse.call(this, monthName, format, strict)`): the complete implementation of the
  exact mode; returns a month index 0–11 or `null`.

=== STUB ===
```javascript
export function localeMonthsParse (monthName, format, strict) {
    // TODO: implement according to the specification
}
```
