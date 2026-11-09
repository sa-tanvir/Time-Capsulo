You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `isFQDN(str, options)` in `src/lib/isFQDN.js`

## 1. Component overview

Public validator of the validator.js library (`validator.isFQDN`). It checks whether a string
is a fully qualified domain name such as `domain.com` or `xn--froschgrn-x9a.com`. It is also
used by `isEmail` (for the domain part of an address) and `isURL` (for the host), which pass
their own options object through.

## 2. Functional requirements

1. Validate the input type first: if `str` is not a string, throw the `TypeError` produced by
   `assertString` (see context).
2. Options (missing or `undefined` keys take the defaults from `default_fqdn_options`):
   `require_tld` (default `true`), `allow_underscores` (default `false`),
   `allow_trailing_dot` (default `false`). Each is tested for truthiness.
3. If `allow_trailing_dot` is truthy and the string ends with `.`, exactly one trailing dot is
   ignored (`'example.com.'` is then valid, `'example.com..'` is not).
4. Split the (possibly shortened) string on `.` into labels. If **any** label, including the
   last one, is longer than 63 characters (UTF-16 code units), the result is `false`.
5. If `require_tld` is truthy, the last label is the top-level domain (TLD) and is checked
   separately; there must be at least one other label (so `'abc'` is invalid). The TLD
   is valid only if it either
   - consists of at least 2 characters, each an ASCII letter (any case) or a code unit in the
     range U+00A1–U+FFFF (`'com'`, `'COM'`, `'рф'`, `'端端'`), or
   - is `xn` (any case) followed by at least 2 characters from ASCII letters, digits and `-`
     (`'xn--p1ai'`);
   and in addition it must not contain any whitespace character (as matched by JS `\s`), nor
   any of U+2002–U+200B, U+202F, U+205F, U+3000, U+FEFF, nor the code units U+DB40 or U+DC20.
   Digits are not allowed in a TLD of the first form (`'1com'`, `'c0m'` are invalid). The TLD
   is not subject to the label rules of step 6.
   All these checks work on UTF-16 **code units**, not on code points: "a code unit in
   U+00A1–U+FFFF" includes each half of a surrogate pair (0xD800–0xDFFF), so a single
   supplementary character such as `'𝐚'` (two code units) already satisfies the
   two-character minimum, and is accepted unless one of its code units is 0xDB40 or 0xDC20
   (e.g. U+E0020, encoded as 0xDB40 0xDC20, is rejected; so is any character whose high or
   low surrogate is one of these two values).
6. Every remaining label (all labels when `require_tld` is falsy) must satisfy, after removing
   all `_` characters from it when `allow_underscores` is truthy:
   - it is non-empty and every code unit is an ASCII letter, an ASCII digit, `-`, or in the
     range U+00A1–U+FFFF (so `!`, `*`, `/`, spaces, `_` (unless allowed) are rejected);
   - it contains no full-width form U+FF01–U+FF5E (e.g. `'ｇｍａｉｌ'`);
   - it does not start or end with `-` (`'-a.com'`, `'a-.com'` are invalid; `'foo--bar.com'`
     is valid).
7. Return `true` when all checks pass, otherwise `false`.

## 3. Input specification

- `str`: a string of any length (possibly empty, possibly containing any Unicode text).
  Non-string values are invalid and cause a `TypeError`.
- `options`: optional; `undefined` or a plain object with any subset of the three boolean
  options. Other keys (e.g. URL options passed by `isURL`) are ignored.

## 4. Output specification

A boolean. Examples (default options unless stated):

- valid: `'domain.com'`, `'dom.plato'`, `'a.domain.co'`, `'foo--bar.com'`,
  `'xn--froschgrn-x9a.com'`, `'rebecca.blackfriday'`, `'m端ller.com'`
- invalid: `'abc'` (no TLD), `'256.0.0.0'` (numeric TLD), `'_.com'`, `'*.some.com'`,
  `'s!ome.com'`, `'domain.com/'`, `'/more.com'`, `'bar.com.'` (trailing dot not allowed),
  `'.com'` and `'a..b.com'` (empty label), `'invalid.co m'` (space in TLD),
  `'ｇｍａｉｌ.com'` (full-width label), `'foo.c'` (TLD too short)
- `isFQDN('example.com.', { allow_trailing_dot: true })` → `true`
- `isFQDN('localhost', { require_tld: false })` → `true`
- `isFQDN('my_host.com')` → `false`; `isFQDN('my_host.com', { allow_underscores: true })` → `true`
- `isFQDN('a'.repeat(64) + '.com')` → `false`; with 63 `a`s → `true`

## 5. Edge cases and constraints

- The empty string is invalid (with or without `require_tld`, since a label would be empty).
- With `require_tld: false`, every label including the last is checked by step 6, so
  `'1.2.3.4'` is valid then, while `'a.'` is invalid unless `allow_trailing_dot` is set.
- Underscore removal applies only to non-TLD labels; a label consisting only of underscores
  becomes empty and is therefore invalid.
- Characters are examined per UTF-16 code unit; supplementary characters (surrogate pairs) are
  inside the accepted U+00A1–U+FFFF range for labels.
- The function may fill default option values into the passed options object (as `merge`
  does); it must not otherwise modify it. It is synchronous and side-effect free otherwise.

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isFQDN.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import merge from './util/merge';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(none)
```

## Variables declared at the same scope level (you may use them)

```
const default_fqdn_options = {
  require_tld: true,
  allow_underscores: false,
  allow_trailing_dot: false,
};
```

## Behaviour of the imported helpers

- `assertString(input)` (default export of `./util/assertString`): returns nothing if `input` is a
  primitive string or a `String` object; otherwise throws a `TypeError` with the message
  `Expected string but received <type>.` (e.g. `a number`, `null`, `Array`).
- `merge(obj = {}, defaults)` (default export of `./util/merge`): for every key of `defaults`
  whose value in `obj` is `undefined`, copies the default into `obj`; returns `obj` (the same
  object, mutated; a new `{}` when `obj` is `undefined`). Keys already present with a
  non-`undefined` value (including `null`/`false`) are kept.

=== STUB ===
```javascript
export default function isFQDN(str, options) {
    // TODO: implement according to the specification
}
```
