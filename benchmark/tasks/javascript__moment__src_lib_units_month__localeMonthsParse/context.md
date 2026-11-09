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
