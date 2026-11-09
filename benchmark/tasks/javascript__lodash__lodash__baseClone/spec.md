# Functional specification: `baseClone(value, bitmask, customizer, key, object, stack)` in `lodash.js`

## 1. Component overview

Internal engine of lodash 4.17.14's cloning methods. The public wrappers are:
`_.clone(v)` = `baseClone(v, CLONE_SYMBOLS_FLAG)`, `_.cloneDeep(v)` =
`baseClone(v, CLONE_DEEP_FLAG | CLONE_SYMBOLS_FLAG)`, `_.cloneWith(v, c)` and
`_.cloneDeepWith(v, c)` (same flags plus a customizer). It is also used with
`CLONE_DEEP_FLAG` alone by `_.matches`, `_.matchesProperty`, `_.conforms` and
`_.iteratee` (to snapshot their `source`), and with deep | flat | symbols by
`_.omit`. It returns a copy of `value`: shallow (one level) or deep (recursive,
preserving shared and circular references), keeping prototypes, and handling
arrays, plain objects, class instances, `arguments`, maps, sets, dates, regexes,
boxed primitives, symbols objects, array buffers, data views, typed arrays and
Node buffers. Values that cannot be cloned are handled specially.

## 2. Functional requirements

Flags: `CLONE_DEEP_FLAG` (1) deep; `CLONE_FLAT_FLAG` (2) also copy inherited
enumerable properties into a plain object; `CLONE_SYMBOLS_FLAG` (4) also copy own
(or, with flat, own and inherited) enumerable symbol properties. `key` and
`object` are the property key of `value` and its parent container on recursive
calls (both absent at the top level); `stack` maps already visited sources to
their clones.

1. **Customizer.** If `customizer` is given, call it first: at the top level
   (no `object`) with exactly one argument, `customizer(value)`; on recursive
   calls as `customizer(value, key, object, stack)`. If it returns anything but
   `undefined`, that is the result for this value (no further processing).
2. **Primitives** (anything for which `isObject` is false: `null`, `undefined`,
   numbers, strings, booleans, symbol primitives) are returned as is.
3. **Arrays:** the result starts as `initCloneArray(value)` (same length; it
   keeps the `index`/`input` properties of `RegExp#exec` results). Shallow mode:
   fill it with the elements (`copyArray`) and return it; extra non-index
   properties are not copied.
4. **Other objects** (non-arrays):
   - Node `Buffer` (`isBuffer(value)` is true): return
     `cloneBuffer(value, isDeep)` directly. This test comes before every
     tag-based rule below (a Buffer's tag is `Uint8Array`, but it is never
     cloned as a typed array), and before the stack lookup of rule 5.
   - All other (non-Buffer) objects are classified by `getTag(value)` as in the following three items.
   - Plain objects, class instances and `arguments` objects (tags `Object`,
     `Arguments`), and **functions at the top level** (no `object`): the result
     starts as `{}` when flat mode is on or `value` is a function, otherwise as
     `initCloneObject(value)` (a new object with the same prototype, or `{}` for
     prototype objects and objects whose `constructor` is not a function).
     Shallow mode: copy own enumerable string keys with `baseAssign` and own
     enumerable symbols with `copySymbols` (flat: own + inherited with
     `baseAssignIn` and `copySymbolsIn`) and return the result. (Note that the
     shallow copy always includes symbols, whatever the symbols flag.)
   - Tags that `cloneableTags` marks as not cloneable (errors, weak maps,
     functions nested inside a container, and any unknown tag such as DOM
     nodes): return `value` itself when there is a parent `object`, otherwise a
     new empty `{}`.
   - Other cloneable tags (`Map`, `Set`, `Date`, `RegExp`, `Boolean`, `Number`,
     `String`, `Symbol` objects, `ArrayBuffer`, `DataView`, typed arrays): the
     result starts as `initCloneByTag(value, tag, isDeep)` (maps and sets start
     empty; typed arrays and data views share the original buffer in shallow
     mode and copy it in deep mode; regexes keep `lastIndex`).
5. **Circular / shared references.** Create `stack` (a new `Stack`) if absent.
   If `stack.get(value)` is truthy, return that earlier clone. Otherwise record
   `stack.set(value, result)` before filling `result`.
6. **Map and Set contents:** for a set, add the clone of every element (each
   cloned with `key` = the element and `object` = the set); for a map, set each
   original key (keys are not cloned) to the clone of its value (`key` = the
   map key, `object` = the map). This also happens in shallow mode (elements are
   then cloned shallowly).
7. **Properties:** for arrays, every index `0 .. length-1` (holes read as
   `undefined`); for other values the keys given by `keys` (own enumerable
   string keys), or `keysIn` in flat mode, or with the symbols flag
   `getAllKeys` / `getAllKeysIn` (adding enumerable symbols). For each such key,
   clone `value[key]` recursively with the same `bitmask`, `customizer`, the key,
   `value` as parent and the shared `stack`, and store it with
   `assignValue(result, key, clone)`. (Boxed primitives, dates, regexes, maps and
   sets thereby keep their expando properties, also in shallow mode.)
8. Return the result.

## 3. Input specification

`value`: any value. `bitmask`: an integer combining the flags above.
`customizer`: optional function. `key`, `object`, `stack`: omitted by top-level
callers; supplied on recursion (`stack` is a `Stack` with `get`/`set`/`has`/`delete`).

## 4. Output specification

The clone (or the original value / customizer result as described). Examples:

- `_.clone([{a: 0}, {b: 1}])` -> new array whose elements are the same objects
- `_.cloneDeep` of `o = {foo: {b: {c: {d: o}}}, bar: {b: o.foo.b}}` -> `r` with
  `r.bar.b === r.foo.b`, `r.foo.b.c.d === r`, `r !== o`
- `_.clone(new Foo)` and `_.cloneDeep(new Foo)` are `instanceof Foo` (also when
  `Foo.prototype.constructor` was set to `Object`; not when it is `null`)
- `_.clone(Foo.prototype)` with `Foo.prototype.b = 1` -> plain `{b: 1}`
- `_.clone(Foo)` (a function with own `c`) -> `{c: Foo.c}`; `_.clone(new Error)` ->
  `{}`; `_.cloneDeep({a: fn, b: {c: err}})` -> new objects holding the same `fn`
  and `err` references
- `_.clone(/c/g)` after `exec('abcde')` keeps `lastIndex` 3; a clone of
  `/c/.exec('abcde')` keeps `index` 2 and `input` `'abcde'`
- `Object(false)`, `Object(1)`, `Object('a')` with expando `a: 1` -> clones keep `a`
- `_.clone(sym) === sym`; `_.clone(Object(sym))` is a new symbol object
- typed array view `new Int8Array(buf, 8, 1)`: clone has same `byteOffset` and
  `length`; `clone.buffer === view.buffer` only for `_.clone`
- symbol keys: own enumerable symbols are copied (deep-cloned for `cloneDeep`),
  inherited or non-enumerable symbols are not copied as own properties
- `_.cloneDeepWith(new Foo, c)` calls `c(object)` then `c(1, 'a', object, stack)`
  (the last argument is a `Stack`); `_.cloneWith` calls only `c(object)`
- a customizer returning `value` for non-plain objects makes `_.cloneWith(fn, c)`
  return `fn` itself

## 5. Edge cases and constraints

- Never mutates `value` (only `stack` and the new result are written).
- Deeply circular graphs (hundreds of mutually referencing containers) must be
  handled; every source object is cloned once and shared references stay shared.
- Linear in the number of visited properties/elements.
