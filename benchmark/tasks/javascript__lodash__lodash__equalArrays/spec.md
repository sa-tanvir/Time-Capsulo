# Functional specification: `equalArrays(array, other, bitmask, customizer, equalFunc, stack)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14's deep-equality engine (`_.isEqual`,
`_.isEqualWith`, `_.isMatch`, `_.isMatchWith`, `_.matches`, `_.matchesProperty`).
`baseIsEqualDeep` calls it to compare two arrays, two typed arrays or two
buffers, and the map/set branch of `equalByTag` calls it with the entry lists of
two maps (`[key, value]` pairs) or the value lists of two sets. It compares the
elements index by index (or, in *unordered* mode, by finding a distinct partner
for every element), recursing into nested values through `equalFunc`, and it
supports *partial* comparison (used by `_.isMatch`), a user customizer, and
circular references via `stack`.

## 2. Functional requirements

Flags in `bitmask`: `COMPARE_PARTIAL_FLAG` (1) and `COMPARE_UNORDERED_FLAG` (2).

1. **Length.** Let `n = array.length` and `m = other.length`. If `n != m`, return
   `false`, except in partial mode where `m > n` is allowed (`other` may have
   extra elements).
2. **Cycles.** If `stack.get(array)` is truthy **and** `stack.get(other)` is
   truthy, the pair is already being compared further up: return whether
   `stack.get(array) == other`, without examining elements.
3. Otherwise record the pair in both directions (`stack.set(array, other)` and
   `stack.set(other, array)`), compare the elements, then remove both entries
   with `stack['delete'](array)` and `stack['delete'](other)` before returning,
   whatever the outcome (also after an early mismatch).
4. **Elements.** For each index `i` from `0` to `n - 1` in order (non-index
   properties are ignored; holes read as `undefined`), with `a = array[i]` and
   `o = other[i]`:
   - If `customizer` is given, call it first: in partial mode as
     `customizer(o, a, i, other, array, stack)`, otherwise as
     `customizer(a, o, i, array, other, stack)`. If it returns anything other than
     `undefined`, a truthy value means "element equal, go on" and a falsy value
     means "not equal": the result is `false` and comparison stops.
   - Otherwise (no customizer, or it returned `undefined`):
     - **ordered mode** (unordered flag not set): the element matches when
       `a === o` or `equalFunc(a, o, bitmask, customizer, stack)` is truthy;
     - **unordered mode**: scan **all** of `other` (indices `0 .. m - 1`, in
       order) for the first index `j` not yet claimed by an earlier element of
       `array` such that `a === other[j]` or
       `equalFunc(a, other[j], bitmask, customizer, stack)`; claim `j` (each index
       of `other` can be claimed at most once) and continue. If no such `j`
       exists, the element does not match.
     If the element does not match, the result is `false` and comparison stops.
5. Return `true` if every element matched, otherwise `false` (a primitive
   boolean).

## 3. Input specification

- `array`, `other`: arrays (possibly sparse, possibly with extra non-index
  properties, possibly containing themselves), typed arrays, buffers, or the
  converted entry/value arrays of maps/sets. Contents are arbitrary values.
- `bitmask`: integer combining the two flags above (0 for `_.isEqual`; partial and
  unordered for `_.isMatch`; unordered is added for map/set contents).
- `customizer`: optional function; its return value is interpreted as above.
- `equalFunc`: the recursive deep-equality function
  `(value, other, bitmask, customizer, stack) => boolean` (normally `baseIsEqual`).
- `stack`: a `Stack` instance (key/value cache with `get`, `set`, `has`,
  `delete`) shared by the whole comparison.

## 4. Output specification

`true` or `false`. Examples through the public API:

- `isEqual([1, 'a', {e: 1}], [1, 'a', {e: 1}])` -> `true`;
  `isEqual([1, 2, 3], [3, 2, 1])` -> `false`; `isEqual([1, 2], [1, 2, 3])` -> `false`
- `isEqual(Array(1), [undefined])` -> `true` (sparse arrays compare as dense)
- arrays with identical elements but different extra properties
  (`a.b = 1` vs `a.b = 2`) -> `true`
- `var a = [1]; a[1] = a; var b = [1]; b[1] = b;` -> `isEqual(a, b)` is `true`;
  pushing different values afterwards makes them unequal
- typed arrays / buffers with equal elements and the same type -> `true`
- `isEqual(new Set([1, 2]), new Set([2, 1]))` -> `true` (unordered);
  maps with the same entries in different insertion order -> `true`
- partial (`_.isMatch`): `isMatch({a: [1, 2, 3]}, {a: [3, 1]})` -> `true`;
  `isMatch({a: [1, 2]}, {a: [2, 2]})` -> `false` (each element of `other` can
  be used only once); `isMatch({a: [1, 2]}, {a: []})` -> `true`
- `isEqualWith(['a'], ['b'], v => typeof v == 'string' || undefined)` -> `true`;
  with a customizer returning `false` for strings, `isEqualWith(['a'], ['a'], c)`
  is `false`; a customizer returning `undefined` changes nothing
- `isEqualWith` customizer receives, for array elements, exactly
  `(a[i], o[i], i, array, other, stack)`

## 5. Edge cases and constraints

- Must not mutate `array` or `other`; the only side effects are on `stack`
  (always restored) and calls to `customizer`/`equalFunc`.
- Stop at the first mismatch (no further customizer or `equalFunc` calls).
- Strict identity (`===`) of two elements is enough for a match without calling
  `equalFunc`; `NaN` handling is left to `equalFunc`.
- Ordered comparison is linear in `n` (plus nested work); unordered comparison
  may be quadratic.
