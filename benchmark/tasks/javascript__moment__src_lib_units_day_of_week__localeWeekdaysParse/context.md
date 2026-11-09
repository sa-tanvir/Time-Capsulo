# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/units/day-of-week.js`

## Imports / includes available in this file

```
import { addFormatToken } from '../format/format';
import { addUnitAlias } from './aliases';
import { addUnitPriority } from './priorities';
import { addRegexToken, match1to2, matchWord, regexEscape } from '../parse/regex';
import { addWeekParseToken } from '../parse/token';
import toInt from '../utils/to-int';
import isArray from '../utils/is-array';
import indexOf from '../utils/index-of';
import hasOwnProp from '../utils/has-own-prop';
import { createUTC } from '../create/utc';
import getParsingFlags from '../create/parsing-flags';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( format )
(anonymous) ( input , week , config , token )
(anonymous) ( isStrict , locale )
cmpLenRev ( a , b )
computeWeekdaysParse ( )
getSetDayOfWeek ( input )
getSetISODayOfWeek ( input )
getSetLocaleDayOfWeek ( input )
handleStrictParse ( weekdayName , format , strict )
localeWeekdays ( m , format )
localeWeekdaysMin ( m )
localeWeekdaysShort ( m )
parseIsoWeekday ( input , locale )
parseWeekday ( input , locale )
shiftWeekdays ( ws , n )
weekdaysMinRegex ( isStrict )
weekdaysRegex ( isStrict )
weekdaysShortRegex ( isStrict )
```

## Variables declared at the same scope level (you may use them)

```
var defaultWeekdaysRegex = matchWord;
var defaultWeekdaysShortRegex = matchWord;
var defaultWeekdaysMinRegex = matchWord;
```

## Instance state (`this` is a `Locale` object; the function is installed as `Locale.prototype.weekdaysParse`)

Attributes read or written:

| attribute | type | meaning |
|---|---|---|
| `this._weekdaysParseExact` | boolean or undefined | locale config flag `weekdaysParseExact`; when truthy, parsing is exact (string comparison) and handled by `handleStrictParse` |
| `this._weekdaysParse` | array (indices 0–6) or undefined | lazily filled per-weekday cache of the lenient pattern (a `RegExp`) for weekday `i`; created as `[]` on first use |
| `this._fullWeekdaysParse` | array or undefined | lazily filled cache of the strict full-name `RegExp` per weekday |
| `this._shortWeekdaysParse` | array or undefined | lazily filled cache of the strict short-name `RegExp` per weekday |
| `this._minWeekdaysParse` | array or undefined | lazily filled cache of the strict min-name `RegExp` per weekday |

(`handleStrictParse` stores lower-cased name strings in `_weekdaysParse`, `_shortWeekdaysParse` and
`_minWeekdaysParse` instead; a locale uses one mode or the other, never both.)

Sibling methods / helpers used:

- `this.weekdays(m, format)`, `this.weekdaysShort(m, format)`, `this.weekdaysMin(m, format)`:
  given a moment `m`, return the locale's full / short / min name of `m`'s weekday (for an empty
  format string the "standalone" form is used when a locale distinguishes forms).
- `createUTC([2000, 1])` (imported from `../create/utc`): a UTC moment for 2000-02-01;
  `.day(i)` on a moment sets the day of the week to `i` (0 = Sunday … 6 = Saturday) and returns
  the moment, so `createUTC([2000, 1]).day(i)` is a moment whose weekday is `i`.
- `handleStrictParse(weekdayName, format, strict)` (same file, call it with
  `handleStrictParse.call(this, weekdayName, format, strict)`): the complete implementation of the
  exact mode; returns a weekday index 0–6 or `null`.
