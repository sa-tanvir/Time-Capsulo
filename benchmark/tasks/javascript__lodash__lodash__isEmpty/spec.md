# Functional specification: `isEmpty(value)` in `lodash.js`

## 1. Component overview

Public lodash 4.17.14 method `_.isEmpty(value)`: checks whether `value` is an
empty object, collection, map, or set. It is also available in chains
(`_({}).isEmpty()` returns the unwrapped boolean `true`).

## 2. Functional requirements

Return a boolean decided by the first matching rule:

1. `value` is `null` or `undefined` -> `true`.
2. `value` is *array-like* (see `isArrayLike`: not a function, and has a `length`
   that is a number and an integer in `[0, Number.MAX_SAFE_INTEGER]`) **and** is
   one of: an array, a string primitive, an object whose `splice` property is a
   function (jQuery/MooTools-style query collections), a Node.js `Buffer`, a typed
   array, or an `arguments` object -> `true` exactly when its `length` is `0`.
3. `value` is a `Map` or a `Set` (as classified by `getTag`, so maps/sets from
   other realms count too) -> `true` exactly when its `size` is `0`.
4. `value` is a prototype object (see `isPrototype`: it is the `prototype` of its
   own `constructor`, or it is `Object.prototype`) -> `true` exactly when it has
   no own enumerable string keys other than `constructor` (as computed by
   `baseKeys`).
5. Otherwise -> `false` if `value` has at least one **own** enumerable string-keyed
   property (found by `for..in` enumeration, filtered with
   `Object.prototype.hasOwnProperty`), else `true`. Inherited enumerable
   properties do not make a value non-empty.

Consequences that must hold:

- Booleans, numbers (including `NaN`), symbols, regexes, functions without own
  enumerable properties, `Date`s, and errors without own enumerable properties
  are empty (`true`).
- A plain object with a `length` property is judged by rule 5, not by its length:
  `{ length: 0 }` is **not** empty, `{ length: '0' }` is not empty.
- Objects whose `length` is not a valid array-like length (negative, larger than
  `MAX_SAFE_INTEGER`, or non-number), e.g. an instance whose prototype has
  `length = -1`, are judged by rule 5 (so `new Foo` with no own keys is empty).

## 3. Input specification

`value`: any JavaScript value (primitive, array, string, `arguments`, typed array,
`Buffer`, `Map`, `Set`, plain or class-instance object, prototype object,
function, `null`/`undefined`, or absent).

## 4. Output specification

A boolean primitive (`true` or `false`).

Examples:

- `isEmpty(null)`, `isEmpty(undefined)`, `isEmpty()`, `isEmpty(false)`, `isEmpty(0)`,
  `isEmpty(NaN)`, `isEmpty('')`, `isEmpty([])`, `isEmpty({})` -> `true`
- `isEmpty(true)`, `isEmpty(1)`, `isEmpty(/x/)`, `isEmpty(Symbol('a'))`,
  `isEmpty(Array.prototype.slice)` -> `true`
- `isEmpty(Buffer.alloc(0))` -> `true`; `isEmpty(Buffer.alloc(1))` -> `false`
- `isEmpty([0])`, `isEmpty({ a: 0 })`, `isEmpty('a')` -> `false`
- `isEmpty({ length: 0 })` -> `false`
- `arguments` object of `(1, 2, 3)` -> `false`
- `function Foo() {}; Foo.prototype = { constructor: Foo };` ->
  `isEmpty(Foo.prototype)` is `true`; after `Foo.prototype.a = 1` it is `false`
- `function Foo(els) { Array.prototype.push.apply(this, els); }`
  `Foo.prototype = { length: 0, splice: Array.prototype.splice };` ->
  `isEmpty(new Foo([]))` is `true`
- `isEmpty(new Map)` -> `true`; after `map.set('a', 1)` -> `false` (same for `Set`
  with `add`)
- `function Foo() {}; Foo.prototype.length = -1;` -> `isEmpty(new Foo)` is `true`
  (same with `length = Number.MAX_SAFE_INTEGER + 1`)

## 5. Edge cases and constraints

- Must not mutate `value` and must not call methods on it (the `splice` property
  is only type-checked, never invoked).
- For rule 5 the answer is determined by the existence of any own enumerable key;
  there is no need to collect all keys.
- Typed arrays and buffers are judged by `length`, maps and sets by `size`;
  extra own properties on them do not matter.
- Always returns a primitive boolean, never a truthy/falsy non-boolean.
