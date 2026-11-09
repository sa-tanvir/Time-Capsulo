# Functional specification: `isIn(str, options)` in `src/lib/isIn.js`

## 1. Component overview

Public validator of the validator.js library (`validator.isIn`). It checks whether a string is
one of a set of allowed values. The set may be given as an array of values, as an object whose
own keys are the allowed values, or as a string in which the value must occur as a substring.

## 2. Functional requirements

1. If `str` is not a string, throw the `TypeError` produced by `assertString` (see context).
2. **Array** (`options` is a real array, i.e. `Object.prototype.toString` gives
   `'[object Array]'`): convert every element with the `toString` helper (see context) and
   return `true` if `str` is strictly equal to one of the converted values, else `false`.
   The conversion means, for example: numbers and booleans compare by their string form
   (`5` → `'5'`, `true` → `'true'`); `null` and `undefined` become `''`; plain objects become
   `'[object Object]'`; objects with their own `toString` method become its result; objects
   whose `toString` property is not a function become `'[object Object]'`; functions declared
   without parameters become `''`.
3. **Object** (otherwise, when `typeof options === 'object'`): return whether `options` has an
   own property named `str` (`hasOwnProperty`); inherited properties such as `'toString'` do not
   count; property values are irrelevant. Note that `null` falls into this branch and, because
   it has no properties, accessing them throws a `TypeError`.
4. **String or other indexable value** (otherwise, when `options` is truthy and has an
   `indexOf` method): return whether `options.indexOf(str)` is ≥ 0, i.e. for a string whether
   `str` occurs as a substring (the empty string occurs in every non-empty string).
5. In every other case (`options` omitted/`undefined`, numbers, booleans, the empty string,
   functions without `indexOf`) return `false`.

## 3. Input specification

- `str`: a string (non-strings throw `TypeError`).
- `options`: an array of arbitrary values (strings, numbers, booleans, `null`, objects), a plain
  object, a string, or any other value. Collections may have thousands of entries and strings
  may be long.

## 4. Output specification

A boolean (or a thrown `TypeError` as described). Examples:

- `isIn('foo', 'foobar')`, `'bar'`, `'foobar'`, `''` → `true`; `'foobarbaz'`, `'barfoo'` → `false`
- `isIn('foo', ['foo', 'bar'])` → `true`; `'foobar'`, `'barfoo'`, `''` → `false`
- `isIn('1', ['1', '2', '3'])` → `true`; `'4'`, `''` → `false`
- with `['1', '2', '3', { foo: 'bar' }, () => 5, { toString: 'test' }]`: `'1'`, `'2'`, `'3'`,
  `''` → `true` (the function gives `''`), `'4'` → `false`; `'[object Object]'` → `true`
- `isIn('null', [null])` → `false`; `isIn('', [null])` → `true`; `isIn('5', [5])` → `true`
- `isIn('foo', { foo: 1, bar: 2, foobar: 3 })` → `true`; `'foobarbaz'`, `'barfoo'`, `''`,
  `'toString'` → `false`
- `isIn('2', { 1: 3, 2: 0, 3: 1 })` → `true` (value `0` does not matter); `'4'` → `false`
- `isIn('foo')` → `false`; `isIn('', '')` → `false`; `isIn('1', 1)` → `false`;
  `isIn('foo', null)` → throws `TypeError`

## 5. Edge cases and constraints

- Must not modify `options` (when an array is given, build any converted values separately).
- Matching is exact and case-sensitive for arrays and objects; only the string form matches
  substrings.
- Synchronous, no side effects.
