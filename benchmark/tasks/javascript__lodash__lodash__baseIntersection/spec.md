# Functional specification: `baseIntersection(arrays, iteratee, comparator)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14 behind `_.intersection(...arrays)`,
`_.intersectionBy(...arrays, iteratee)` and `_.intersectionWith(...arrays,
comparator)`. Given a list of arrays, it returns the unique values of the first
array that are present in every other array, in the order of the first array.
Equality is SameValueZero by default, may be applied to keys computed by an
iteratee, or may be a custom comparator.

## 2. Functional requirements

1. `arrays` holds at least one array; `arrays[0]` is the *first* array and the
   rest are the *other* arrays. (Callers have already replaced non-array-like
   *other* arguments by empty arrays, so the result is then `[]`; when the first
   argument is not array-like the public wrappers return `[]` without calling
   this function.)
2. **Keys.** With `iteratee`, the key of an element is `iteratee(element)`
   (one argument). The keys of all elements of the other arrays are computed
   first, array by array starting from the **last** array and moving towards the
   second one, each in index order; afterwards the first array is scanned and
   each of its elements gets its key when it is reached. E.g.
   `intersectionBy([2.1, 1.2], [2.3, 3.4], f)` first calls `f(2.3)`. Without
   iteratee, keys are the elements themselves.
3. **Membership.** Walk the first array in index order. An element is added to
   the result when:
   - its key is not equal to the key of an element already added (so the result
     is duplicate-free), and
   - for every other array, some element of that array has an equal key.
   Equality is SameValueZero without `comparator` (strict equality, except `NaN`
   equals `NaN` and `-0` equals `+0`; objects only equal themselves). With
   `comparator` (callers never pass an iteratee at the same time), elements are
   equal when `comparator(candidate, other)` is truthy, where `candidate` is the
   element of the first array and `other` is an element of the other array or an
   already-added result element.
4. **Zero sign.** Without a comparator, a `-0` from the first array is added as
   `+0`; with a comparator the original value is kept (`-0` stays `-0`).
5. The stored values are the original elements of the first array (never keys).
6. The scan may stop early once the result is as long as the shortest input
   array (no more values can be added); this must not change the result.
7. Return a new array; inputs are not modified.

## 3. Input specification

- `arrays`: an array of one or more arrays / array-likes (`arguments` objects
  allowed), each of any length (possibly large), containing any values.
- `iteratee`: optional key function (shorthands already converted).
- `comparator`: optional function `(a, b) => boolean`.

## 4. Output specification

A new duplicate-free array of elements of the first array, in first-occurrence
order.

Examples (through the public wrappers):

- `intersection([2, 1], [2, 3])` -> `[2]`
- `intersection([2, 1, 2, 3], [3, 4], [3, 2])` -> `[3]`
- `intersection([1, 1, 3, 2, 2], [5, 2, 2, 1, 4], [2, 1, 1])` -> `[1, 2]`
- `intersection([1, 1, 3, 2, 2])` -> `[1, 3, 2]` (single array: just unique values)
- `intersection([0, 1, null, 3], argsOf123)` -> `[1, 3]`, and
  `intersection(argsOf123, [0, 1, null, 3])` -> `[1, 3]`
- `intersection([-0, 0], [0])` and `intersection([-0, 0], [-0])` -> `[0]` (positive
  zero), also when the second array is 200 copies of `0` or `-0`
- `intersection([1, NaN, 3], [NaN, 5, NaN])` -> `[NaN]` (also against 200 `NaN`s)
- `intersection([o], 200 copies of o)` -> `[o]`; `intersection([0..199], [1])` -> `[1]`
- `intersectionBy([2.1, 1.2], [2.3, 3.4], Math.floor)` -> `[2.1]`
- `intersectionBy([{x:1}], [{x:2}, {x:1}], o => o.x)` -> `[{x:1}]`
- `intersectionWith([{x:1,y:2},{x:2,y:1}], [{x:1,y:1},{x:1,y:2}], _.isEqual)` -> `[{x:1,y:2}]`
- `intersectionWith([-0], [0], _.eq)` -> `[-0]` (also against 200 zeros)

## 5. Edge cases and constraints

- Must not mutate inputs.
- Must be efficient for large inputs: without a comparator, the total cost should
  be roughly linear in the combined length of all arrays (testing each candidate
  by scanning whole other arrays is too slow when they hold thousands of
  elements). With a comparator, pairwise comparison is unavoidable.
- Empty first array -> `[]`; any empty other array -> `[]`.
