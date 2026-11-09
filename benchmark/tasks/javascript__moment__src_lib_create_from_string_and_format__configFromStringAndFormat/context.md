# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/create/from-string-and-format.js`

## Imports / includes available in this file

```
import { configFromISO, configFromRFC2822 } from './from-string';
import { configFromArray } from './from-array';
import { getParseRegexForToken }   from '../parse/regex';
import { addTimeToArrayFromToken } from '../parse/token';
import { expandFormat, formatTokenFunctions, formattingTokens } from '../format/format';
import checkOverflow from './check-overflow';
import { HOUR } from '../units/constants';
import { hooks } from '../utils/hooks';
import getParsingFlags from './parsing-flags';
```

## Other functions defined in the same file (signatures only; you may call them)

```
hooks.ISO_8601 ( )
hooks.RFC_2822 ( )
meridiemFixWrap ( locale , hour , meridiem )
```

## The config object and the imported helpers

`config` is moment's internal creation config (`moment(input, format, locale, strict)` builds it):

| property | meaning |
|---|---|
| `config._i` | the input (normally a string) |
| `config._f` | the format string, or the constants `hooks.ISO_8601` / `hooks.RFC_2822` (functions, compare by identity) |
| `config._locale` | the `Locale` to parse with |
| `config._strict` | strict parsing flag |
| `config._useUTC`, `config._isUTC` | UTC mode flags |
| `config._a` | date-part array `[year, month (0-based), day, hour, minute, second, millisecond]` filled by the token parsers; index `HOUR` (= 3) is the hour |
| `config._meridiem` | meridiem text (e.g. `'pm'`) stored by the `a`/`A` token parser, if any |
| `config._pf` | parsing flags object, always accessed through `getParsingFlags(config)` (creates it on first use with defaults `empty: false, unusedTokens: [], unusedInput: [], overflow: -2, charsLeftOver: 0, nullInput: false, invalidMonth: null, invalidFormat: false, userInvalidated: false, iso: false, parsedDateParts: [], meridiem: null, rfc2822: false, weekdayMismatch: false`). Token parsers may also set `bigHour: true` (12-hour tokens `h`/`hh`), `invalidMonth`, `_overflowDayOfYear`, etc. |

Helpers (imported):

- `configFromISO(config)` / `configFromRFC2822(config)`: complete parsing of `config._i` as
  ISO 8601 / RFC 2822 (they set everything themselves).
- `expandFormat(format, locale)`: replaces the locale's long-date macros (`LT`, `LTS`, `L`, `LL`,
  `LLL`, `LLLL` and lower-case variants) in `format` by the locale's format strings, repeatedly.
- `formattingTokens`: a global regular expression; `string.match(formattingTokens)` splits a
  format string into tokens: bracketed literals (`'[at]'`), real tokens (`'YYYY'`, `'MM'`, `'Do'`,
  `'HH'`, `'Z'`, …), and single other characters (`'-'`, `' '`, `':'`). Returns `null` for `''`.
- `formatTokenFunctions`: object whose keys are the real formatting tokens (literals are not keys).
- `getParseRegexForToken(token, config)`: the (unanchored) `RegExp` that recognises the input for
  `token` (depends on strictness and locale); for a literal token it matches the literal text.
- `addTimeToArrayFromToken(token, input, config)`: runs the token's parser, which stores the parsed
  value into `config._a` (or `config._w`, `config._tzm`, `config._meridiem`, `config._dayOfYear`,
  `config._d`, flags …); does nothing when `input` is `null`/`undefined` or the token has no parser.
- `meridiemFixWrap(locale, hour, meridiem)` (same file): converts a 12-hour `hour` plus meridiem
  text to a 24-hour value using the locale (returns `hour` unchanged when `meridiem` is
  `null`/`undefined`).
- `configFromArray(config)`: builds `config._d` (a `Date`) from `config._a` and the other parsed
  fields (defaulting missing parts, applying `_tzm`, setting `_nextDay` for 24:00, weekday checks).
- `checkOverflow(config)`: sets `getParsingFlags(config).overflow` to the index of the first
  out-of-range part of `config._a`, or `-1`.
- `hooks`: the moment function itself; `hooks.ISO_8601` and `hooks.RFC_2822` are defined in this
  file as marker functions.
