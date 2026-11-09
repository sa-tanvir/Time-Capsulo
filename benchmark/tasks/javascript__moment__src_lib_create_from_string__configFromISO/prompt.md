You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/create/from-string.js`

## Imports / includes available in this file

```
import { configFromStringAndFormat } from './from-string-and-format';
import { createUTCDate } from './date-from-array';
import { configFromArray } from './from-array';
import { hooks } from '../utils/hooks';
import { deprecate } from '../utils/deprecate';
import getParsingFlags from './parsing-flags';
import {defaultLocaleMonthsShort} from '../units/month';
import {defaultLocaleWeekdaysShort} from '../units/day-of-week';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( config )
calculateOffset ( obsOffset , militaryOffset , numOffset )
checkWeekday ( weekdayStr , parsedInput , config )
configFromRFC2822 ( config )
configFromString ( config )
extractFromRFC2822Strings ( yearStr , monthStr , dayStr , hourStr , minuteStr , secondStr )
preprocessRFC2822 ( s )
untruncateYear ( yearStr )
```

## Variables declared at the same scope level (you may use them)

```
var extendedIsoRegex = /^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;
var basicIsoRegex = /^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;
var tzRegex = /Z|[+-]\d\d(?::?\d\d)?/;
var isoDates = [
    ['YYYYYY-MM-DD', /[+-]\d{6}-\d\d-\d\d/],
    ['YYYY-MM-DD', /\d{4}-\d\d-\d\d/],
    ['GGGG-[W]WW-E', /\d{4}-W\d\d-\d/],
    ['GGGG-[W]WW', /\d{4}-W\d\d/, false],
    ['YYYY-DDD', /\d{4}-\d{3}/],
    ['YYYY-MM', /\d{4}-\d\d/, false],
    ['YYYYYYMMDD', /[+-]\d{10}/],
    ['YYYYMMDD', /\d{8}/],
    // YYYYMM is NOT allowed by the standard
    ['GGGG[W]WWE', /\d{4}W\d{3}/],
    ['GGGG[W]WW', /\d{4}W\d{2}/, false],
    ['YYYYDDD', /\d{7}/]
];
var isoTimes = [
    ['HH:mm:ss.SSSS', /\d\d:\d\d:\d\d\.\d+/],
    ['HH:mm:ss,SSSS', /\d\d:\d\d:\d\d,\d+/],
    ['HH:mm:ss', /\d\d:\d\d:\d\d/],
    ['HH:mm', /\d\d:\d\d/],
    ['HHmmss.SSSS', /\d\d\d\d\d\d\.\d+/],
    ['HHmmss,SSSS', /\d\d\d\d\d\d,\d+/],
    ['HHmmss', /\d\d\d\d\d\d/],
    ['HHmm', /\d\d\d\d/],
    ['HH', /\d\d/]
];
var aspNetJsonRegex = /^\/?Date\((\-?\d+)/i;
var rfc2822 = /^(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s)?(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{2,4})\s(\d\d):(\d\d)(?::(\d\d))?\s(?:(UT|GMT|[ECMP][SD]T)|([Zz])|([+-]\d{4}))$/;
var obsOffsets = {
    UT: 0,
    GMT: 0,
    EDT: -4 * 60,
    EST: -5 * 60,
    CDT: -5 * 60,
    CST: -6 * 60,
    MDT: -6 * 60,
    MST: -7 * 60,
    PDT: -7 * 60,
    PST: -8 * 60
};
```

## The config object and the helpers used

`config` is moment's internal creation config (built by `moment(input, …)` / `moment.utc(…)`):
`config._i` is the input string, `config._f` the format (undefined when called for
`moment(string)`, or `hooks.ISO_8601` when called from format parsing), `config._locale`,
`config._strict`, `config._useUTC`. Validity is recorded in `config._isValid` (`false` = invalid;
when it stays unset, validity is computed later from the parsing flags).

- `getParsingFlags(config)` (imported from `./parsing-flags`): returns the parsing-flags object
  of the config (`config._pf`), creating it with default values on first use. Its boolean `iso`
  flag records that the input looked like ISO 8601.
- `configFromStringAndFormat(config)` (imported from `./from-string-and-format`): parses
  `config._i` according to the moment format string in `config._f` and fills the config
  (date parts, `Date`, flags). Format tokens used here: `YYYY`, `YYYYYY` (6-digit signed year),
  `MM`, `DD`, `DDD` (day of year), `GGGG`/`WW`/`E` (ISO week-year, week, weekday), `HH`, `mm`,
  `ss`, `SSSS` (fraction), `Z` (offset or `Z`), bracketed literals such as `[W]`.
- In the variables above: `extendedIsoRegex` / `basicIsoRegex` recognise a whole ISO string
  (optional leading whitespace); capture group 1 is the date part, group 2 the date/time separator
  (`T` or space), group 3 the time part, group 4 the zone part. `isoDates` and `isoTimes` are
  ordered lists of `[momentFormat, regex]` (dates may have a third element `false` meaning "no time
  allowed with this date form"); `tzRegex` recognises a zone designator.

=== STUB ===
```javascript
export function configFromISO(config) {
    // TODO: implement according to the specification
}
```
