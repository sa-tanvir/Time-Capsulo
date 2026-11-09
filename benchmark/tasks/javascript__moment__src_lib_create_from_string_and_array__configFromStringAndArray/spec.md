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
