# Functional specification: `baseDifference(array, values, iteratee, comparator)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14 behind `_.difference(array, ...values)`,
`_.differenceBy`, `_.differenceWith`, `_.without(array, ...values)` and the
`_.xor*` family. It returns the elements of `array` that do not occur in
`values` (after the public wrappers have flattened all exclusion arrays into the
single array `values`). Order and duplicates of `array` are preserved; the
comparison may go through an iteratee (key function) or a custom comparator.

## 2. Functional requirements

1. If `array` has length `0`, return a new empty array immediately (no iteratee
   calls).
2. If `iteratee` is given, first compute the keys of all `values` by calling
   `iteratee(v)` (exactly one argument) for each element of `values` in index
   order; then, while scanning `array`, compute each element's key with
   `iteratee(element)`. So the very first iteratee call receives `values[0]`
   (e.g. `differenceBy([2.1, 1.2], [2.3, 3.4], f)` first calls `f(2.3)`).
   Without an iteratee, the key of every value is the value itself.
3. Walk `array` once in index order (holes read as `undefined`). An element is
   **excluded** when its key matches one of the keys of `values`:
   - **without comparator**: match by SameValueZero (strict equality, except
     `NaN` matches `NaN` and `-0` matches `+0`); objects match only themselves;
   - **with comparator** (callers never pass an iteratee at the same time):
     match when `comparator(element, v)` is truthy for some `v` in `values`
     (the `array` element first, the `values` element second).
   Every non-excluded element is appended to the result, including repeated
   ones (`difference([1, 1, 2], [2])` gives `[1, 1]`).
4. Zero sign: without a comparator, a kept `-0` is appended as `+0`; with a
   comparator, kept elements are appended unchanged (`-0` stays `-0`).
5. The stored element is always the original `array` element, never its key.
6. Return a new array; `array` and `values` are not modified.

## 3. Input specification

- `array`: an array or array-like (e.g. `arguments`) of any values; the public
  wrappers pass `[]` when the input is not array-like.
- `values`: an array of values to exclude (may be empty, and may be large, e.g.
  hundreds of thousands of elements, with repeats).
- `iteratee`: optional function `(value) => key` (shorthands already converted).
- `comparator`: optional function `(arrVal, othVal) => boolean`.

## 4. Output specification

A new array with the kept elements of `array` in original order.

Examples (as seen through the public wrappers):

- `difference([2, 1], [2, 3])` -> `[1]`
- `difference([2, 1, 2, 3], [3, 4], [3, 2])` -> `[1]` (values = `[3, 4, 3, 2]`)
- `difference([-0, 0], [0])` and `difference([-0, 0], [-0])` -> `[]`
- `difference([-0, 1], [1])` -> `[0]` (positive zero; `toString` gives `'0'`)
- `difference([1, NaN, 3], [NaN, 5, NaN])` -> `[1, 3]`
- `array1 = [0..200, a, b, c]`, `array2 = [0..199, b, c, a]` (objects `a,b,c`) ->
  `[200]`
- 200 copies of `object1` as values, array `[object1, object2]` -> `[object2]`
- 200 `NaN`s as values, array `[1, NaN, 3]` -> `[1, 3]`
- `differenceBy([2.1, 1.2], [2.3, 3.4], Math.floor)` -> `[1.2]`
- `differenceBy([{x:2},{x:1}], [{x:1}], o => o.x)` -> `[{x:2}]`
- `differenceWith([{x:1,y:2},{x:2,y:1}], [{x:1,y:2}], _.isEqual)` -> `[{x:2,y:1}]`
- `differenceWith([-0, 1], [1], _.eq)` -> `[-0]` (also with 200 ones as values)
- `difference(args123, ...)` where the other arguments are not array-like ->
  `[1, 2, 3]`; `difference([1, null, 3], argsOf123)` -> `[null]`

## 5. Edge cases and constraints

- Must not mutate inputs.
- Must be efficient when both inputs are large: without a comparator the total
  cost should be roughly linear in `array.length + values.length` (a scan of all
  of `values` for every element of `array` is too slow when `values` holds
  thousands of elements). With a comparator, pairwise comparison is unavoidable.
- The iteratee is called once per element of `values` and once per element of
  `array` (only when `array` is non-empty).
