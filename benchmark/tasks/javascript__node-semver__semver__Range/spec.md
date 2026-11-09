# Functional specification: `Range(range, options)` (constructor) in `semver.js`

## 1. Component overview

Constructor of the `Range` class of node-semver (exported as `semver.Range`). It parses an npm version-range string
such as `'>=1.2.7 <1.3.0 || 2.x'` into a disjunction of comparator sets and computes its canonical text. Nearly every
range helper (`satisfies`, `validRange`, `toComparators`, `maxSatisfying`, `minVersion`, `gtr`/`ltr`, `intersects`)
starts with `new Range(...)`.

## 2. Functional requirements

1. **Options normalisation.** If `options` is falsy or not an object, replace it by
   `{loose: !!options, includePrerelease: false}`; objects are used as given.
2. **Range input.** If `range` is already a `Range`: when `range.loose === !!options.loose` and
   `range.includePrerelease === !!options.includePrerelease`, return that **same object**; otherwise return
   `new Range(range.raw, options)`.
3. **Comparator input.** If `range` is a `Comparator`, return `new Range(range.value, options)`.
4. **Call without `new`.** When invoked as a plain function, return `new Range(range, options)` (normalised options).
5. **Initialisation** of a new instance from a string:
   - `this.options = options`, `this.loose = !!options.loose`,
     `this.includePrerelease = !!options.includePrerelease`, `this.raw = range` (the original string);
   - split the string on `||` together with any whitespace around it; trim each part and convert it with
     `this.parseRange(part)`; errors thrown there propagate (strict mode: `TypeError('Invalid comparator: ...')`);
   - drop parts whose comparator array is empty (only possible in loose mode, when every token was invalid);
     keep the remaining arrays, in order, as `this.set`;
   - if no set remains, throw `new TypeError('Invalid SemVer Range: ' + range)`;
   - finally call `this.format()` to fill `this.range`.

## 3. Input specification

- `range`: a range string (any length; may contain many `||` alternatives and many comparators), a `Range`, or a
  `Comparator`.
- `options`: `undefined`, a boolean/any non-object (loose flag), or `{loose, includePrerelease}`.

## 4. Output specification

A `Range` instance (possibly the input object, see 2). Examples of the resulting `range` text:

| input | options | `range` |
|---|---|---|
| `'1.0.0 - 2.0.0'` | - | `>=1.0.0 <=2.0.0` |
| `''`, `'*'`, `'x'`, `'>=*'` | - | `''` (one set with an `ANY` comparator) |
| `'\|\|'` | - | `'\|\|'` (two `ANY` sets) |
| `'0.1.20 \|\| 1.2.4'` | - | `0.1.20\|\|1.2.4` |
| `'1.2.x \|\| 2.x'` | - | `>=1.2.0 <1.3.0\|\|>=2.0.0 <3.0.0` |
| `'1.2.3 \|\|  \|\| 2'` | - | `1.2.3\|\|\|\|>=2.0.0 <3.0.0` (3 sets) |
| `'~> 1'`, `'^ 1'` | - | `>=1.0.0 <2.0.0` |
| `'^ 1.2 ^ 1'` | - | `>=1.2.0 <2.0.0 >=1.0.0 <2.0.0` |
| `'>= v1.2.3'` | - | `>=1.2.3` (`toString()` gives the same) |
| `'  1.2.3  '` | - | `1.2.3` |
| `'~1.02.03beta'` | loose | `>=1.2.3-beta <1.3.0` |
| `'>=01.02.03'` | - | throws `TypeError` (invalid comparator) |
| `'>=1.2.3 garbage'` | loose / strict | `>=1.2.3` / throws `TypeError('Invalid comparator: garbage')` |
| `'blerg'` | loose | throws `TypeError('Invalid SemVer Range: blerg')` |
| `'blerg'` | strict | throws `TypeError('Invalid comparator: blerg')` |

`this.set` holds the Comparator arrays, e.g. `new Range('1 2').set` has one set with the values
`['>=1.0.0', '<2.0.0', '>=2.0.0', '<3.0.0']`.

## 5. Edge cases and constraints

- The input string is stored unchanged in `raw` (needed when the range is re-created with other options).
- Must not modify an input `Range` or `Comparator`.
- Work should be linear in the number of comparators.
