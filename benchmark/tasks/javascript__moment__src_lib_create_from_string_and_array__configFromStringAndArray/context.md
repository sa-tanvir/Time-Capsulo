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
