# Functional specification: `arrayToObject(source, options)` in `lib/utils.js`

## 1. Component overview

Internal utility of the `qs` library (exported as `utils.arrayToObject`). It
converts an array into an ordinary object keyed by index. `utils.merge` uses it
when an array that was built while parsing a query string must be merged with
non-array data, e.g. `qs.parse('foo[0]=bar&foo[bad]=baz')` gives
`{ foo: { 0: 'bar', bad: 'baz' } }` and `qs.parse('a[0]=b&a[1]=c', { arrayLimit: 0 })`
gives `{ a: { 0: 'b', 1: 'c' } }`.

## 2. Functional requirements

1. Create a new object. If `options` is given and `options.plainObjects` is truthy,
   the object must have a `null` prototype (as created by `Object.create(null)`);
   otherwise it is a normal object literal (prototype `Object.prototype`).
2. For every index `i` from `0` to `source.length - 1`, in ascending order, if
   `source[i]` is not `undefined`, set the property `i` of the new object to
   `source[i]`.
3. Entries whose value is `undefined` (explicitly `undefined` or holes of a sparse
   array) are omitted: no property is created for them. All other values,
   including `null`, `0`, `''`, `false`, `NaN`, objects and arrays, are copied
   by reference (no deep copy).
4. Return the new object.

## 3. Input specification

- `source`: an array (possibly sparse) or any array-like value with a numeric
  `length` and indexed access. Only indices `0 .. length-1` are considered; any
  non-index properties of the array are ignored.
- `options`: optional; `undefined`, `null`, or an object. Only its `plainObjects`
  property is read.

## 4. Output specification

A fresh object whose own enumerable keys are the string forms of the indices of
the non-`undefined` elements.

Examples:

- `arrayToObject(['a', 'b'])` -> `{ 0: 'a', 1: 'b' }`
- `arrayToObject(['bar'], {})` -> `{ 0: 'bar' }` (ordinary prototype)
- `arrayToObject(['b'], { plainObjects: true })` -> null-prototype object `{ 0: 'b' }`
  (so that, while parsing `'a[]=b&a[c]=d'` with `plainObjects: true`, the result
  for `a` is a null-prototype object `{ 0: 'b', c: 'd' }`)
- a sparse array of length 3 whose only element is `'b'` at index 2 ->
  `{ 2: 'b' }` (only one property; this is why
  `qs.parse('a[2]=b&a[99999999]=c')` returns `{ a: { 2: 'b', 99999999: 'c' } }`
  with no entries for indices 0 and 1)
- `arrayToObject([null, undefined, 0])` -> `{ 0: null, 2: 0 }`
- `arrayToObject([])` -> `{}`

## 5. Edge cases and constraints

- Must not mutate `source` or `options` and must never write to `source` (no
  setters on it may be invoked); elements are only read.
- The returned object is always a new object, never `source` itself, and is never
  an array.
- Values are not cloned; nested objects in the result are the same references as in
  `source`.
- `options.plainObjects` is tested for truthiness only; other option properties are
  irrelevant.
