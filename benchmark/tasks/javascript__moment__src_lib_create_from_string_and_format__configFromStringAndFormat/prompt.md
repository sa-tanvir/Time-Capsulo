You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `configFromStringAndFormat(config)` in `src/lib/create/from-string-and-format.js`

## 1. Component overview

Core of moment.js's format-based parsing: `moment('2016-01-02 23:40', 'YYYY-MM-DD HH:mm')`,
`moment(str, fmt, true)` (strict) and `moment.utc(str, fmt)` all end up here. The function walks
through the tokens of the format, consumes the matching pieces of the input string, lets each
token's parser store its value in the config, records bookkeeping flags used later for validity
(`isValid()`), for picking the best of several formats, and for `parsingFlags()`, and finally
builds the `Date`. It returns nothing; all results are written into `config` (see `context.md`).

## 2. Functional requirements

1. **Special constants.** If `config._f` is `hooks.ISO_8601`, delegate entirely to
   `configFromISO(config)`; if it is `hooks.RFC_2822`, to `configFromRFC2822(config)`. Nothing else
   happens in these cases.
2. **Reset.** Set `config._a` to a new empty array and the parsing flag `empty` to `true`.
3. **Tokens.** Convert the input to a string (`'' + config._i`). Expand the format with
   `expandFormat(config._f, config._locale)` and split it into tokens with `formattingTokens`
   (no tokens for an empty format).
4. **Consume the input, token by token, in order.** Keep a "remaining input" (initially the
   whole string) and a running count of consumed characters.
   - Search the remaining input for the token's regular expression from `getParseRegexForToken`
     (it may match anywhere, not only at the start). The matched text (first match) is the
     token's parsed input; an empty match counts as "nothing parsed".
   - If something was parsed: the text in front of the first occurrence of the matched text is
     skipped — when it is non-empty, append it to the flag array `unusedInput`. The remaining
     input becomes the text after that occurrence, and the matched length is added to the
     consumed count.
   - If the token is a real formatting token (a key of `formatTokenFunctions`): when something
     was parsed set flag `empty` to `false`, otherwise append the token to the flag array
     `unusedTokens`; then call `addTimeToArrayFromToken(token, parsedInput, config)`, where
     `parsedInput` is exactly the first match's text: the empty string `''` when the regular
     expression matched an empty string, and `undefined` when it did not match at all. (The
     distinction matters: the helper ignores `undefined`/`null` input but passes `''` on to the
     token's parser.)
   - If the token is a literal (not a key of `formatTokenFunctions`) and nothing was parsed, append
     it to `unusedTokens` only in strict mode (`config._strict` truthy).
5. **Leftovers.** Set flag `charsLeftOver` to the input length minus the consumed count. If the
   remaining input is non-empty, append it to `unusedInput`.
6. **12-hour clock flag.** If flag `bigHour` is exactly `true` and the parsed hour
   (`config._a[HOUR]`) is greater than 0 and at most 12, reset `bigHour` to `undefined` (a 12-hour
   token was used with a valid 1–12 value).
7. **Snapshot.** Set flag `parsedDateParts` to a shallow copy of `config._a` and flag `meridiem`
   to `config._meridiem`.
8. **Meridiem.** Replace the hour entry of `config._a` by the value `meridiemFixWrap` returns for
   the config's locale, the current hour entry and the stored meridiem text.
9. **Finish.** Call `configFromArray(config)` and then `checkOverflow(config)`.

## 3. Input specification

- `config`: object with `_i` (input; usually a string, any value is stringified), `_f` (format
  string or one of the two constants), `_locale` (a `Locale`), `_strict` (boolean or undefined),
  `_useUTC`/`_isUTC`; it may or may not already have a parsing-flags object `_pf`. Formats may use
  any moment parsing tokens, bracketed literals and long-date macros.

## 4. Output specification

No return value (`undefined`). After the call `config` holds `_a`, `_d`, flags in `_pf`, and
whatever the token parsers stored. Examples (`en` locale):

- `'2016-01-02T23:40:40.678'` with `'YYYY-MM-DDTHH:mm:ss.SSS'` → `_a = [2016, 0, 2, 23, 40, 40, 678]`,
  `empty: false`, `unusedTokens: []`, `unusedInput: []`, `charsLeftOver: 0`, `overflow: -1`,
  `parsedDateParts` = the same 7 parts.
- `'2012-05.25'` with `'YYYY-MM-DD'`: the `-` literal before `DD` is not found right away; the
  `.` is skipped (`unusedInput: ['.']`) — in strict mode the unmatched literal `'-'` is added to
  `unusedTokens` (strict result invalid), in non-strict mode it is not.
- `'2012 seven'` with `'YYYY MMM'` → `invalidMonth: 'seven'` (set by the month parser),
  `parsedDateParts: [2012]`.
- `'2012-05-25 16 PM'` with `'YYYY-MM-DD h A'` → `bigHour` stays `true` (16 > 12);
  `'2012-05-25 4 PM'` with `'YYYY-MM-DD h A'` → `bigHour` is reset and the hour becomes 16.
- `'2016-01-02 junk'` with `'YYYY-MM-DD'` → `unusedInput: [' junk']`, `charsLeftOver: 5`.
- `'2016-01-02'` with `'YYYY-MM-DD [extra] HH'` → `unusedTokens: ['HH']` (plus `'[extra]'` and the
  space tokens in strict mode).
- `''` with `'YYYY-MM-DD'` → nothing parsed: `empty: true`, `unusedTokens: ['YYYY', 'MM', 'DD']`
  (non-strict), `charsLeftOver: 0`.
- `'2013-02-08 09:30:26'` with `hooks.ISO_8601` → handled by `configFromISO`.

## 5. Edge cases and constraints

- The input string is never modified in `config._i`; consumption works on a local copy.
- Only flags/fields described above are written directly; everything else comes from the called
  helpers.
- Inputs may be long (hundreds of tokens); each token is processed once.
- Results do not depend on the host time zone beyond what `configFromArray` does.

=== CONTEXT ===
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

=== STUB ===
```javascript
export function configFromStringAndFormat(config) {
    // TODO: implement according to the specification
}
```
