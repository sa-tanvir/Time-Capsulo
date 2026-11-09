# Functional specification: `baseUniq(array, iteratee, comparator)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14 that creates a duplicate-free copy of an array.
It implements `_.uniq(array)`, `_.uniqBy(array, iteratee)`,
`_.uniqWith(array, comparator)`, the `_.union*` family (applied to the
concatenation of the input arrays) and the final step of the `_.xor*` family; it
is also used internally by many other lodash methods. Only the first occurrence
of each distinct element (or distinct *key*, when an iteratee is given) is kept,
in original order.

## 2. Functional requirements

1. Walk `array` from index `0` to `length - 1` exactly once, in order. Holes
   are read as `undefined`.
2. For each element `value`, its *key* is `iteratee(value)` when `iteratee` is
   given (called with exactly one argument, once per element, in index order),
   otherwise `value` itself.
3. **Without `comparator`:** two keys are equal according to SameValueZero:
   strict equality, except that `NaN` equals `NaN` and `-0` equals `+0`. Objects,
   symbols and functions are equal only to themselves; the number `2`, the string
   `'2'`, `Object('2')` and `Object(2)` are all distinct. An element is kept if
   its key differs from the keys of all elements kept so far. A kept element that
   is `-0` is stored in the result as `+0` (so `uniq([-0, 0])` gives `[0]`, whose
   `toString` is `'0'`).
4. **With `comparator`** (callers never pass `iteratee` together with it): an
   element is kept unless `comparator(value, kept)` returns truthy for some
   element `kept` already in the result (current element first, previously kept
   element second). The sign of zero is preserved in this mode
   (`uniqWith([-0, 0], eq)` gives `[-0]`).
5. With an iteratee, the element that is stored is the original `value` (the
   first one producing each key), never the key: `uniqBy(largeArrayOfEqualPairs,
   String)` returns `[firstPair]`, the very same object reference.
6. Return a new array; never return or modify the input.

## 3. Input specification

- `array`: an array (or array-like with numeric indices and `length`), possibly
  empty, containing any values: numbers including `NaN`/`-0`, strings, booleans,
  `null`, `undefined`, symbols (including well-known ones), objects, arrays.
  Arrays may be large (thousands to hundreds of thousands of elements).
- `iteratee`: optional function `(value) => key`; property shorthands (`'a'`,
  `0`, `['0','a']`, ...) have already been converted to functions by callers.
- `comparator`: optional function `(a, b) => boolean`, e.g. `_.isEqual` or `_.eq`.

## 4. Output specification

A new array containing the kept elements in their original relative order.

Examples:

- `[2, 1, 2]` -> `[2, 1]`; `[1, 2, 2]` -> `[1, 2]`
- `[{a:2},{a:3},{a:1},{a:2},{a:3},{a:1}]` (six distinct objects) -> all six
- `[NaN, NaN]` -> `[NaN]`; `[-0, 0]` -> `[0]` (positive zero)
- 200 elements made of runs of `0`, one object `o`, `'a'` -> `[0, o, 'a']`
- runs of `null, undefined, false, true, NaN` -> `[null, undefined, false, true, NaN]`
- 200 distinct `Symbol()`s -> all of them, in order
- runs of `'2'`, `2`, `Object('2')`, `Object(2)` (same object per run) -> those 4
- with iteratee `o => o.a` on the six objects above -> the first three objects
- with iteratee `x => x[0]` on `[['a'], ['a'], ['b']]` -> `[['a'], ['b']]`
- comparator `_.isEqual` on `[{x:1,y:2},{x:2,y:1},{x:1,y:2}]` -> first two objects
- comparator `_.eq` on `[-0, 0]` (or a long alternating `-0, 0` array) -> `[-0]`
- `[]` -> `[]`

## 5. Edge cases and constraints

- Must not mutate `array`.
- The iteratee is called exactly once per element and the comparator only with
  (current, previously kept) pairs; neither is called when the array is empty.
- Must be efficient for large arrays: without a comparator, total time should be
  roughly linear in `length` even when most elements are distinct (a quadratic
  pairwise scan is too slow for arrays of 100,000 distinct values). With a
  comparator, pairwise comparison is unavoidable.
