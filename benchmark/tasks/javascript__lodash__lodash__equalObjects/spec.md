# Functional specification: `equalObjects(object, other, bitmask, customizer, equalFunc, stack)` in `lodash.js`

## 1. Component overview

Internal helper of lodash 4.17.14's deep-equality engine (`_.isEqual`,
`_.isEqualWith`, `_.isMatch`, `_.isMatchWith`, `_.matches`,
`_.matchesProperty`). `baseIsEqualDeep` calls it for two values that are both
"plain-ish" objects (tag `[object Object]`; `arguments` objects are treated the
same way, as are `Object.create(null)` objects and class instances). It compares
the objects' own enumerable string keys **and** own enumerable symbol keys and
their values, recursing through `equalFunc`, supports *partial* matching (used by
`_.isMatch`), a user customizer, circular references via `stack`, and finally
checks the constructors.

## 2. Functional requirements

Flag in `bitmask`: `COMPARE_PARTIAL_FLAG` (1); the unordered flag (2) is only
passed through to `equalFunc`.

1. **Key lists.** Let `objKeys = getAllKeys(object)` and `othKeys =
   getAllKeys(other)` (own enumerable string keys in `keys` order, followed by
   own enumerable symbols). In full (non-partial) mode, if their lengths differ,
   return `false`.
2. **Key presence.** Every key of `objKeys` must be present on `other`: as an
   **own** property in full mode (`hasOwnProperty`), or merely reachable with the
   `in` operator (own or inherited) in partial mode. Otherwise return `false`.
   (This check is done before anything else that has side effects: no customizer
   call and no stack change happen when it fails.)
3. **Cycles.** If `stack.get(object)` is truthy **and** `stack.get(other)` is
   truthy, return whether `stack.get(object) == other` without comparing values.
4. Otherwise record the pair both ways (`stack.set(object, other)`,
   `stack.set(other, object)`) and remove both entries
   (`stack['delete'](object)`, `stack['delete'](other)`) before returning,
   whatever the outcome.
5. **Values.** For each key `k` of `objKeys` **in order**, with
   `ov = object[k]` and `tv = other[k]`:
   - If `customizer` is given, call it: in partial mode as
     `customizer(tv, ov, k, other, object, stack)`, else as
     `customizer(ov, tv, k, object, other, stack)`. A result other than
     `undefined` decides this key: truthy = equal, falsy = not equal.
   - Without a decisive customizer result, the values are equal when
     `ov === tv` or `equalFunc(ov, tv, bitmask, customizer, stack)` is truthy.
   - On the first unequal key the result is `false` and comparison stops.
6. **Constructor check** (only if all values were equal, only in full mode, and
   only if no key named `'constructor'` was among the compared keys): read
   `object.constructor` and `other.constructor`. If they differ (`!=`), and both
   objects have a `constructor` property (own or inherited, `in` operator), the
   objects are unequal **unless** both constructors are functions that are
   instances of themselves (i.e. `C instanceof C`, true for `Object` and
   `Function`, so objects from different realms or `Object.create(null)`-style
   objects are not rejected).
7. Return a primitive boolean.

## 3. Input specification

- `object`, `other`: non-null objects with tag `[object Object]` (plain objects,
  class instances, `arguments` objects, null-prototype objects), possibly with
  symbol keys, inherited properties, and circular references.
- `bitmask`: 0 for `_.isEqual`; partial|unordered (1|2) for `_.isMatch`.
- `customizer`: optional function, interpreted as above.
- `equalFunc`: recursive deep-equality function
  `(value, other, bitmask, customizer, stack) => boolean` (normally `baseIsEqual`).
- `stack`: a `Stack` instance (`get`, `set`, `has`, `delete`) shared by the
  comparison.

## 4. Output specification

`true` or `false`. Examples through the public API:

- `isEqual({a: 1, b: 2}, {b: 2, a: 1})` -> `true` (key order irrelevant)
- `isEqual({a: 1, b: 2}, {a: 1, b: 2, c: 3})` -> `false`
- `isEqual({a: {b: [1]}}, {a: {b: [1]}})` -> `true` (nested, via `equalFunc`)
- `isEqual(new Foo, new Foo)` with `function Foo() { this.a = 1; }` -> `true`;
  `isEqual(new Foo, {a: 1})` -> `false` (different constructors);
  `isEqual({constructor: 1}, {constructor: 1})` -> `true`, `{constructor: 1}` vs
  `{constructor: '1'}` -> `false`
- `Object.create(null)` with `a: 1` vs `{a: 1}` -> `true`
- `arguments` object of `(1, 2, 3)` vs `{0: 1, 1: 2, 2: 3}` -> `true`
- symbol keys: `{[s]: {c: 1}}` vs `{[s]: {c: 1}}` -> `true`; a different value
  or an extra enumerable symbol -> `false`; non-enumerable symbols are ignored
- circular: `o1.self = o1; o2.self = o2` with equal other keys -> `true`
- `isEqualWith({0: 'a'}, {0: 'b'}, v => typeof v == 'string' || undefined)` ->
  `true`; with a customizer returning `false` for strings, `{0: 'a'}` vs
  `{0: 'a'}` -> `false`
- partial (`_.isMatch(object, source)`, i.e. `equalObjects(source, objectVal, ...)`):
  `isMatch({a: 1, b: 2}, {a: 1})` -> `true`; an inherited property of the
  inspected object satisfies a source key; `isMatch({a: {b: 2, c: 3}}, {a: {b: 2}})`
  -> `true`; constructors are not checked
- `isEqualWith` customizer arguments for `o1 = {a: [1, 2], b: o2}`,
  `o2 = {a: [1, 2], b: o1}`: `(o1, o2)`, then `(o1.a, o2.a, 'a', o1, o2, stack)`, the
  array elements, then `(o1.b, o2.b, 'b', o1, o2, stack)` and nothing more (the
  cycle is detected).

## 5. Edge cases and constraints

- Must not mutate the objects; `stack` is always restored.
- Stop at the first mismatch.
- `undefined` values count: `{a: undefined}` vs `{b: undefined}` -> `false`.
- Linear in the number of keys (plus nested comparisons).
