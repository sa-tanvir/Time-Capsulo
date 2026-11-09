# Functional specification: `Comparator(comp, options)` (constructor) in `semver.js`

## 1. Component overview

Constructor of the `Comparator` class of node-semver (exported as `semver.Comparator`). A comparator is the atom of
a range: an operator (`<`, `<=`, `>`, `>=`, or none meaning equality) plus a version, or the empty comparator that
matches every version. `Range` builds one Comparator per desugared comparator string; the class is also used
directly (`new Comparator('>=1.2.3')`, `Comparator('>= v1.2.3').toString()`, `semver.intersects(c1, c2)`).

## 2. Functional requirements

1. **Options normalisation.** If `options` is falsy or not an object, replace it by
   `{loose: !!options, includePrerelease: false}`; an object is used as given (same reference, not copied).
2. **Comparator input.** If `comp` is already a `Comparator`:
   - when `comp.loose === !!options.loose`, return that **same object** (no new instance);
   - otherwise continue with `comp = comp.value` (re-parse its text under the new options).
3. **Call without `new`.** When invoked as a plain function (`Comparator('>=1.2.3')`), return
   `new Comparator(comp, options)` with the normalised options.
4. **Initialisation** of the new instance:
   - `this.options = options` (the normalised object), `this.loose = !!options.loose`;
   - parse the text with `this.parse(comp)`, which sets `this.operator` and `this.semver` (see context) and throws
     `TypeError('Invalid comparator: ' + comp)` for text that is not `<op><spaces><version>` or empty. Errors from
     the `SemVer` constructor (e.g. `'Invalid major version'`) also propagate unchanged;
   - set `this.value`: `''` when `this.semver` is the `ANY` sentinel, otherwise `this.operator + this.semver.version`
     (canonical: no spaces, no `v`/`=` prefix, no build metadata).

## 3. Input specification

- `comp`: a comparator string - an optional operator among `<`, `<=`, `>`, `>=`, `=` (`=` is the same as none),
  optional whitespace, then a full version (strict, or loose when `options.loose`) - or the empty string; or an
  existing `Comparator`. Ranges such as `~1.2.3`, `1.2`, `1.x` are **not** comparators (they are rejected).
- `options`: `undefined`, a boolean/any non-object (loose flag), or `{loose, includePrerelease}`.

## 4. Output specification

The constructed (or returned) Comparator. Examples (`value` / `operator` / `semver.version`):

| comp | options | result |
|---|---|---|
| `'>=1.2.3'` | - | `>=1.2.3` / `>=` / `1.2.3` |
| `'>= v1.2.3'` | - | `>=1.2.3` / `>=` / `1.2.3` (`toString()` -> `'>=1.2.3'`) |
| `'=v1.2.3'` | - | `1.2.3` / `''` / `1.2.3` |
| `'<\t2.0.0'` | - | `<2.0.0` / `<` / `2.0.0` |
| `'1.2.3+build.5'` | - | `1.2.3` / `''` / `1.2.3` |
| `''` | - | `''` / `''` / `semver` is `ANY` |
| `'>=01.02.03'` | `true` | `>=1.2.3` / `>=` / `1.2.3` |
| `'>=01.02.03'` | - | throws `TypeError('Invalid comparator: >=01.02.03')` |
| `'~1.2.3'`, `'1.2'`, `'>'`, `' >=1.2.3'` | - | throws `TypeError('Invalid comparator: ...')` |
| `'>=90071992547409910.0.0'` | - | throws `TypeError('Invalid major version')` |

With `c = new Comparator('>=1.2.3')`: `new Comparator(c)` returns `c` itself; `new Comparator(c, true)` returns a
new loose Comparator with the same `value`; both satisfy `test('1.2.4') === true`.

## 5. Edge cases and constraints

- Leading/trailing whitespace around the whole comparator is not accepted in strict or loose mode.
- `includePrerelease` is kept in `this.options` but does not change parsing.
- Must not modify an input Comparator.
