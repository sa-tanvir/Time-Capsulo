# Functional specification: `truncate(string, options)` in `lodash.js`

## 1. Component overview

Public lodash 4.17.14 method `_.truncate([string=''], [options={}])`. It shortens
`string` if it is longer than a maximum length. The last characters of the
shortened string are replaced with an *omission* string (default `'...'`), and
the cut can be moved back to the last occurrence of a *separator*. Lengths are
measured in user-visible symbols when the string contains Unicode symbols that
span several UTF-16 code units (astral characters, combining marks, emoji
sequences), otherwise in code units. Returns the truncated string.

## 2. Functional requirements

1. **Options.** Defaults: `length = 30`, `omission = '...'`, no separator.
   Only if `options` is an object (`isObject`: objects, arrays, functions) are
   options read; any other `options` (e.g. the index number passed by `_.map`)
   is ignored, so `_.map([s, s], _.truncate)` truncates each with defaults.
   Each option is read only if present according to the `in` operator
   (own or inherited):
   - `length`: converted with `toInteger` (`'4'` -> 4, `4.6` -> 4, `''` / `NaN` -> 0;
     objects are coerced through `valueOf`).
   - `omission`: converted to a string with `baseToString`, so an explicitly
     present `null` becomes `'null'` and `undefined` becomes `'undefined'`.
   - `separator`: a `RegExp` or a string (any other value is used via its string
     form). Present-but-`undefined` means "no separator".
2. `string` is converted with `toString` (`null`/`undefined` -> `''`; objects via
   their `toString`, `String` objects to their primitive value).
3. Let the *size* of the string be its number of symbols if it contains Unicode
   symbols (`hasUnicode`), each symbol being one element of `stringToArray`;
   otherwise its `length` in code units.
4. If `length >= size`, return the converted string unchanged.
5. Otherwise let `end = length - stringSize(omission)` (omission measured in
   symbols). If `end < 1` return just the omission (so a `length` of 0 or a
   negative length returns `'...'` with default omission).
6. Take the first `end` symbols (Unicode case) or code units of the string as the
   kept prefix.
7. Without a separator, return `prefix + omission`.
8. With a separator, let `cut` be the position in the original string (in code
   units) right after the kept prefix.
   - **RegExp separator:** if the remainder of the string starting at `cut` does
     *not* begin with a match of the separator (no match at all, or first match
     at a position > 0), find the **last** match of the separator inside the
     prefix, scanning matches left to right from the start of the prefix (as a
     global search does); if one exists, shorten the prefix to end just before
     that match. Non-global regexes must behave like their global version with
     the same source and flags (e.g. `/,? +/` and `/,? +/g` give the same
     result). A caller's global regex may have its `lastIndex` reset/used, but
     the result must not depend on its initial `lastIndex`.
   - **String separator:** if the original string does not contain the separator
     exactly at position `cut`, shorten the prefix to end just before the
     separator's last occurrence in the prefix, if it occurs there.
   - If the remainder begins with the separator, the prefix is kept as is.
   Return `prefix + omission`.

## 3. Input specification

- `string`: usually a string; any value is accepted and coerced as above.
- `options`: optional; object with optional `length` (number-like), `omission`
  (any, stringified), `separator` (RegExp or string); non-objects are ignored.

## 4. Output specification

A string primitive. Examples with `s = 'hi-diddly-ho there, neighborino'`
(31 code units):

- `truncate(s)` -> `'hi-diddly-ho there, neighbo...'`
- `truncate(s, { length: 31 })` and `{ length: 33 }` -> `s` unchanged
- `truncate(s, { length: 24 })` -> `'hi-diddly-ho there, n...'`
- `truncate(s, { omission: ' [...]' })` -> `'hi-diddly-ho there, neig [...]'`
- `truncate(s, { omission: null })` -> `'hi-diddly-ho there, neighbnull'`
- `truncate(s, { omission: undefined })` -> `'hi-diddly-ho there, nundefined'`
- `truncate(s, { length: 4 })` -> `'h...'`
- `truncate(s, { length: 24, separator: ' ' })` -> `'hi-diddly-ho there,...'`
- `truncate(s, { length: 24, separator: /,? +/ })` -> `'hi-diddly-ho there...'`
  (same with `/,? +/g`)
- `truncate(s, { length: 0 })`, `{ length: -2 }` -> `'...'`
- `truncate(s, { length: { valueOf: () => 4.6 } })` -> `'h...'`;
  with `valueOf` returning `'4'` -> `'h...'`; returning `''` or `NaN` -> `'...'`
- `truncate(Object(s), { length: 4 })` -> `'h...'`;
  `truncate({ toString: () => s }, { length: 5 })` -> `'hi...'`
- `truncate(null)`, `truncate(undefined)`, `truncate('')` -> `''`
- Unicode: with leaf `'🍂'` and a ZWJ family emoji `G`,
  `t = 'A ' + leaf + ', ' + G + ', and 🚀'` has 13 symbols:
  `truncate(t, { length: 13 })` -> `t`; `truncate(t, { length: 6 })` ->
  `'A ' + leaf + '...'`. With `h = '💕'` and `{ length: 4, separator: h }`
  (or `RegExp(h)`): `truncate(t, ...)` -> `'A...'`; for `h` repeated 10 times
  the result is `h + '...'` (length 5 code units), because the remainder after
  the prefix begins with the separator.

## 5. Edge cases and constraints

- Never mutates `options` (other than a global separator regex's `lastIndex`) or
  the input.
- Astral characters and grapheme sequences must never be split in the Unicode case.
- `omission` may itself be longer than `length`; then only the omission is
  returned.
- Zero-length regex matches: a RegExp separator that can match the empty
  string (e.g. `/x*/`, `/\b/`, `/(?=,)/`) is supported only when the
  remainder search of rule 8 finds a match at position 0 (then the prefix is
  kept, as for `/x*/`, which always matches empty at 0). If such a separator
  matches the remainder only later and can match empty inside the prefix, the
  behaviour is outside the contract (the original never terminates). Callers
  and tests never do this.
- Linear time in the length of the input string.
