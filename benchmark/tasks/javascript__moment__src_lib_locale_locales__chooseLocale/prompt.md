You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `chooseLocale(names)` in `src/lib/locale/locales.js`

## 1. Component overview

Module-private helper of moment.js's locale registry. When a caller asks for a locale by a list of
preferred names (`moment.locale(['en-au', 'en-gb'])`, `getLocale(['es', 'fr'])`, or a single name
that is not registered as is, e.g. `'fr-CA-does-not-exist'`), `chooseLocale` picks the best
available `Locale`: it tries each requested name from the most specific form to shorter
prefixes, but stops shortening a name early when the next requested name is a more specific
variant that should be tried first. If nothing matches, the current global locale is returned.

## 2. Functional requirements

Process the names in list order. For the name at position `i`:

1. Normalise it with `normalizeLocale` and split it on `-` into parts (`'en-CA-x'` →
   `['en', 'ca', 'x']`). Let `n` be the number of parts.
2. Also normalise and split the following name (position `i + 1`), if there is one and it is
   non-empty after normalisation; otherwise there is no "next" name.
3. For `j = n, n - 1, …, 1`: look up the prefix made of the first `j` parts joined with `-`
   via `loadLocale`. If a locale is found, return it immediately.
   If not, and there is a next name that has at least `j` parts and differs from the current
   name's parts in at least `j - 1` positions (counted with `compareArrays(currentParts,
   nextParts, true)`, which also adds the length difference), stop trying shorter prefixes of the
   current name and continue with the next name. Otherwise continue with the next shorter prefix.
4. When every name has been processed without a match, return `globalLocale`.

So `['en-fake', 'en-CA']` tries `en-fake`, then — because `en-ca` is an equally specific sibling —
skips `en` and tries `en-ca`; whereas `['en-CH', 'fr']` tries `en-ch`, then `en` (found).

## 3. Input specification

- `names`: an array of locale name strings (any case, `-` or `_` separators, any number of
  parts). It may be empty. Elements are non-null strings.
- The function reads the module state `locales` / `globalLocale` (through `loadLocale` and
  directly) and does not modify it, apart from what `loadLocale` itself may load.

## 4. Output specification

A `Locale` object (from `locales`, or `globalLocale`). Examples with registered locales
`en, en-gb, en-ca, fr, fr-ca, es` and global locale `en` (shown as the returned `_abbr`):

- `['non-existent', 'fr', 'also-non-existent']` → `'fr'`; `['es', 'fr', 'also-non-existent']` → `'es'`
- `['fr-crap']` → `'fr'`; `['fr-does-not-exist']` → `'fr'`; `['fr-CA-does-not-exist']` → `'fr-ca'`
- `['en-CH', 'fr']` → `'en'`
- `['en-gb-leeds', 'en-CA']` → `'en-gb'`
- `['en-fake', 'en-CA']` → `'en-ca'`; `['en-fake', 'en-fake2', 'en-ca']` → `'en-ca'`
- `['fake-CA', 'fake-MX', 'fr']` → `'fr'`; `['fake-CA', 'fake-MX', 'fr-fake-fake-fake']` → `'fr'`
- `['en', 'en-CA']` → `'en'` (earlier names win when they match)
- `['ZH_TW']` with `zh-tw` registered → `'zh-tw'`
- `[]` or `['nope']` → the global locale

## 5. Edge cases and constraints

- Only the first `_` of a name is turned into `-` (by `normalizeLocale`).
- The last name never has a "next" name, so all its prefixes down to the first part are tried.
- Lists can be long (hundreds of names); every name is visited at most once and each name
  contributes at most one lookup per part.
- The returned object is the registered `Locale` itself (not a copy).

=== CONTEXT ===
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

=== STUB ===
```javascript
function chooseLocale(names) {
    // TODO: implement according to the specification
}
```
