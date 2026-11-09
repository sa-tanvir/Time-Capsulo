# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/locale/locales.js`

## Imports / includes available in this file

```
import isArray from '../utils/is-array';
import hasOwnProp from '../utils/has-own-prop';
import isUndefined from '../utils/is-undefined';
import compareArrays from '../utils/compare-arrays';
import { deprecateSimple } from '../utils/deprecate';
import { mergeConfigs } from './set';
import { Locale } from './constructor';
import keys from '../utils/keys';
import { baseConfig } from './base-config';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( x )
defineLocale ( name , config )
getLocale ( key )
getSetGlobalLocale ( key , values )
listLocales ( )
loadLocale ( name )
normalizeLocale ( key )
updateLocale ( name , config )
```

## Variables declared at the same scope level (you may use them)

```
var locales = {};
var localeFamilies = {};
var globalLocale;
```

## Behaviour of the helpers and module state

- `locales`: object mapping a locale name (lower case, `-` separated, e.g. `'en'`, `'fr-ca'`) to
  its `Locale` object. `Locale` objects have an `_abbr` property holding that name.
- `globalLocale`: the current global `Locale` (`'en'` unless changed with `moment.locale(...)`).
- `normalizeLocale(key)`: returns `key` lower-cased with the **first** `_` replaced by `-`
  (`'ZH_TW'` → `'zh-tw'`); a falsy `key` is returned unchanged.
- `loadLocale(name)`: returns the `Locale` registered under exactly `name`, or `undefined`. In
  Node.js, when the name is not registered yet it first tries to load the locale file
  `./locale/<name>` (errors are ignored).
- `compareArrays(array1, array2, dontConvert)` (imported): number of positions present in both
  arrays whose elements differ (with `dontConvert` truthy: strict `!==`), plus the difference of
  the two lengths.
