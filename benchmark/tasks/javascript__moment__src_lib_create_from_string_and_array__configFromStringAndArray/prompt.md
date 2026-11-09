You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `configFromStringAndArray(config)` in `src/lib/create/from-string-and-array.js`

## 1. Component overview

Exported step of moment.js parsing used when a string is parsed with an **array of formats**:
`moment('11-02-1999', ['MM-DD-YYYY', 'DD-MM-YYYY'])`. Each format is tried on a separate copy of
the creation config; among the copies that produce a valid date, the one that left the fewest
characters and tokens unused wins, and its state is copied back into `config`. It returns
nothing; the result is written into `config` (see `context.md`).

## 2. Functional requirements

1. **Empty array.** If `config._f` has length 0: set the parsing flag `invalidFormat` to `true`,
   set `config._d` to an invalid `Date` (`new Date(NaN)`) and stop.
2. **Try every format**, in array order. For format number `i`:
   - Create a fresh object and fill it with `copyConfig(newObject, config)`. If `config._useUTC`
     is not `null`/`undefined`, also copy it onto the new object. Set the new object's `_f` to the
     `i`-th format.
     Nothing else is copied or reset: in particular the parsing flags are **not** recreated per
     attempt. If `config` already has a flags object (`_pf`), every attempt shares that same
     object (as `copyConfig` does), so flags written by one attempt (e.g. entries pushed to
     `unusedTokens`) are visible to later attempts and to the scores computed after them. If
     `config` has no `_pf`, each attempt gets its own fresh flags on first use. (In the usual
     `moment(str, [formats])` flow `config` has no `_pf` yet.)
   - Parse it with `configFromStringAndFormat`.
   - If `isValid` says the attempt is invalid, ignore it (it gets no score).
   - Otherwise its score is the attempt's `charsLeftOver` flag plus 10 times the number of entries
     in its `unusedTokens` flag. Store the score in the attempt's parsing flag `score`.
   - The attempt becomes the best one if there is no best yet or its score is **strictly lower**
     than the best score so far (so among equal scores the earliest format wins).
3. **Result.** Copy (with `extend`) all properties of the best attempt onto `config`. If no attempt
   was valid, copy the **last** attempt instead (so the config ends up invalid with that attempt's
   flags and date).
4. `config._f` therefore ends up as the chosen single format (or whatever the parser left there,
   e.g. the concrete ISO format when the ISO constant was chosen).

## 3. Input specification

- `config`: a creation config with `_i` (input string, possibly empty or junk) and `_f` a
  non-null array of formats (strings and/or the ISO/RFC constants), plus `_locale`, `_strict`,
  `_useUTC`/`_isUTC`. The array itself must not be modified.

## 4. Output specification

No return value. Examples (`en` locale; resulting date shown as `MM DD YYYY`, chosen format as `_f`):

- `'11-02-1999'`, `['MM-DD-YYYY', 'DD-MM-YYYY']` → `11 02 1999`
- `'13-11-1999'`, `['MM/DD/YYYY', 'DD/MM/YYYY']` → `11 13 1999` (first format is invalid)
- `'02-01-2000'`, `['DD/MM/YYYY', 'MM/DD/YYYY']` → `01 02 2000` (both valid, equal score: first wins)
- `'11-02-10'`, `['MM-DD-YY HH:mm', 'YY MM DD']` → `02 10 2011` (unused token costs 10)
- `'11-02-10 junk'`, `['MM-DD-YY', 'YY.MM.DD [junk]']` → `02 10 2011` (leftover characters cost)
- `'13-10-98'`, `['DD MM YY', 'DD MM YYYY']` → `_f === 'DD MM YY'`; `'13-10-1998'` → `'DD MM YYYY'`
- `'01'`, `['MM', 'DD']` → `_f === 'MM'`
- `'1994'`, `[moment.ISO_8601, 'MM', 'HH:mm', 'YYYY']` → year 1994; `'17:15'` with the same array → hour 17
- `'gibberish'`, `['YY-MM-DD', 'YY-DD-MM']` → invalid; `'gibberish'`, `[]` → invalid with
  `invalidFormat: true`
- `' '`, `['MM', 'DD']` → invalid
- The winning attempt's flags include `score` (e.g. `0` for an exact match).

## 5. Edge cases and constraints

- The caller's format array is never mutated (`moment('1999-02-13', arr)` leaves `arr` unchanged).
- Each attempt starts from the original inputs of `config`, not from an earlier attempt's result.
- Arrays may contain hundreds of formats; each format is parsed exactly once.

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/create/from-string-and-array.js`

## Imports / includes available in this file

```
import { copyConfig } from '../moment/constructor';
import { configFromStringAndFormat } from './from-string-and-format';
import getParsingFlags from './parsing-flags';
import { isValid } from './valid';
import extend from '../utils/extend';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(none)
```

## The config object and the imported helpers

`config` is moment's internal creation config, built by `moment(input, [formats…], locale, strict)`:
`config._i` input, `config._f` the **array** of formats (strings, or the constants
`moment.ISO_8601` / `moment.RFC_2822`), `config._locale`, `config._strict`, `config._useUTC`,
`config._isUTC`, possibly `config._l`, `config._tzm`, `config._offset`, `config._pf`. The parse
result lives in `config._d` (a `Date`), `config._a`, `config._pf` (parsing flags) and other
fields written by the parsers.

- `copyConfig(to, from)`: copies the creation inputs from `from` to `to` — `_isAMomentObject`,
  `_i`, `_f`, `_l`, `_strict`, `_tzm`, `_isUTC`, `_offset`, `_pf` (the **same** flags object, not a
  copy, and only if `from` has one), `_locale` and plugin-registered properties — skipping
  undefined values; it does not copy `_useUTC`. Returns `to`.
- `configFromStringAndFormat(config)`: parses `config._i` with the single format `config._f`
  (string or ISO/RFC constant) and writes the result into `config`.
- `isValid(config)`: computes (and caches in `config._isValid`) whether a parsed config is valid;
  in strict mode leftover characters / unused tokens make it invalid.
- `getParsingFlags(config)`: the flags object of a config (`config._pf`), created with defaults on
  first use. Relevant flags: `charsLeftOver` (number of input characters not consumed),
  `unusedTokens` (array of format tokens that matched nothing), `invalidFormat` (boolean),
  `score` (set here).
- `extend(a, b)`: copies all own enumerable properties of `b` onto `a` (plus own `toString` /
  `valueOf`), returns `a`.

=== STUB ===
```javascript
export function configFromStringAndArray(config) {
    // TODO: implement according to the specification
}
```
