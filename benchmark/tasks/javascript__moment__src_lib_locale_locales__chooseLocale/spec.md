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
