# Functional specification: `arrayLikeKeys(value, inherited)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14. It produces the list of enumerable string
property names of an *array-like* value. `_.keys(value)` calls it as
`arrayLikeKeys(value)` and `_.keysIn(value)` as `arrayLikeKeys(value, true)`
whenever `isArrayLike(value)` is true (arrays, `arguments` objects, strings and
`String` objects, typed arrays, buffers, plain objects with a valid numeric
`length`, ...). Through `keys`/`keysIn` it is used by `_.forOwn`, `_.forIn`,
`_.findKey`, `_.mapValues`, `_.assign`, `_.clone`, `_.merge`, `_.toPairs`,
`_.values`, `_.isEqual` and many more. The function differs from a plain
`for..in` collection in that the index keys of genuine indexed collections are
always reported, in ascending order, even when the collection is sparse.

## 2. Functional requirements

1. Classify `value` as an *indexed collection* when it is any of: an array
   (`isArray`), an `arguments` object (`isArguments`), a Node.js `Buffer`
   (`isBuffer`), or a typed array (`isTypedArray`). Everything else (string
   primitives, `String` objects, plain array-like objects such as
   `{ '0': 'a', length: 1 }`, functions are never passed) is *not* an indexed
   collection.
2. For an indexed collection of length `n`, the result starts with the strings
   `'0'`, `'1'`, ..., `String(n - 1)` in ascending order, for **every** index
   below `n`, whether or not the element exists (holes in sparse arrays are
   reported as if present: `[1, , 3]` gives `['0', '1', '2']`).
3. Afterwards, append every key produced by enumerating `value` with a
   `for..in` loop (which yields own and inherited enumerable string keys, in the
   engine's enumeration order), keeping a key only if:
   - when `inherited` is falsy, the key is an **own** property of `value`
     (checked with `Object.prototype.hasOwnProperty`); when `inherited` is
     truthy, inherited enumerable keys are kept too;
   - and, only for indexed collections, the key is not one that would duplicate
     or pollute the index list: it is not `'length'`; for buffers it is not
     `'offset'` or `'parent'`; for typed arrays it is not `'buffer'`,
     `'byteLength'` or `'byteOffset'`; and it is not a valid index below `n`
     (a canonical non-negative integer string such as `'0'` or `'17'` whose
     numeric value is less than `n`).
   Keys that look numeric but are not valid indices below `n` (e.g. `'-1'`,
   `'1.5'`, `'01'`, or `'7'` on an `arguments` object of length 3) are
   ordinary keys and are kept, in enumeration order.
4. For values that are not indexed collections, no index list is generated and
   no key is filtered other than by the own/inherited rule; the result is just
   the filtered `for..in` sequence. For a string primitive or `String` object,
   this yields its character indices (`'0'`, `'1'`, ...) followed by any extra
   own (or inherited, if requested) enumerable keys. For `{ '0': 'a', length: 1 }`
   it yields `['0', 'length']`.
5. Return a new array of strings. `value` is never modified.

## 3. Input specification

- `value`: an array-like value (never `null`/`undefined`): array (possibly
  sparse or with extra non-index properties), `arguments` object (strict or
  sloppy), `Buffer`, any typed array (`Int8Array` ... `Float64Array`,
  `Uint8ClampedArray`), string primitive, `String` object, or an object whose
  `length` is an integer in `[0, Number.MAX_SAFE_INTEGER]`.
- `inherited`: optional; truthy to also include inherited enumerable string keys
  (as `_.keysIn` does), falsy/absent for own keys only (as `_.keys` does).

## 4. Output specification

A new array of property-name strings, index keys (for indexed collections) first
in ascending order, then the remaining keys in `for..in` order.

Examples (`f` = `arrayLikeKeys`):

- `f([1, 2, 3])` -> `['0', '1', '2']`
- sparse `var a = [1]; a[2] = 3;` -> `f(a)` is `['0', '1', '2']`
- `var a = [1]; a.a = 1;` -> `['0', 'a']`
- with `Array.prototype.a = 1` set: `f([1])` -> `['0']`, `f([1], true)` -> `['0', 'a']`
- `arguments` object of `(1, 2, 3)` with an extra own property `a` -> `['0', '1', '2', 'a']`
  (strict-mode `arguments` objects behave the same; their `length` is never reported)
- with `Object.prototype.a = 1`: `f(argumentsOf123)` -> `['0','1','2']`,
  `f(argumentsOf123, true)` -> `['0','1','2','a']`
- `f(Object('abc'))` -> `['0', '1', '2']`; `f('abc')` -> `['0', '1', '2']`
- `var s = Object('a'); s.a = 1;` -> `['0', 'a']`; with `String.prototype.a = 1`,
  `f(Object('a'))` -> `['0']` and `f(Object('a'), true)` -> `['0', 'a']`
- `f({ '0': 'a', length: 1 })` -> `['0', 'length']`
- `f(new Uint8Array(2))` -> `['0', '1']`; `f(Buffer.from('ab'))` -> `['0', '1']`
- `f([])` -> `[]`; `f('')` -> `[]`

## 5. Edge cases and constraints

- Holes in arrays and `arguments` objects are reported; the index list depends
  only on `length`, not on which elements exist.
- An own enumerable `length` property (some engines expose one on strict
  `arguments`) must never appear for indexed collections, but must appear for
  plain array-like objects.
- The function must not mutate `value` and must not invoke anything on it other
  than reading `length`, enumerating it, and own-property checks.
- The result is always a fresh array; ordering is significant and must be as
  described (callers such as `_.findKey` and `_.forOwn` depend on it).
- Performance: linear in `length` plus the number of enumerable keys.
