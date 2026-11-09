# Functional specification: `Range.prototype.test(version)` in `semver.js`

## 1. Component overview

Method of the `Range` class of node-semver: decides whether a version satisfies the range. A range is a disjunction
(`||`) of comparator sets stored in `this.set`; the version satisfies the range when it satisfies at least one set.
It is the core of `satisfies(version, range, options)`, `maxSatisfying`, `minSatisfying`, `minVersion`,
`gtr`/`ltr` and the CLI's `-r <range>` filter.

## 2. Functional requirements

1. A falsy `version` (`undefined`, `null`, `''`) gives `false`.
2. A string is converted with `new SemVer(version, this.options)`. If that throws (invalid version, e.g.
   `'not a version'`, `'glorp'`, or a loose-only spelling such as `'1.2.3foo'` on a strict range), return `false` -
   the method never throws for strings.
3. Return `true` as soon as one comparator set of `this.set` is satisfied, as decided by
   `testSet(set, version, this.options)` (all comparators accept the version, plus the prerelease rule). Sets are
   examined in order and the remaining ones are skipped after the first success.
4. If no set is satisfied, return `false`.

## 3. Input specification

- `this`: a constructed `Range` (`set`, `options` used; see context).
- `version`: a `SemVer`, a version string (strict or loose, according to `this.options.loose`), or a falsy value.

## 4. Output specification

A boolean. Examples (`r.test(v)` with `r = new Range(text, options)`):

| range | version | options | result |
|---|---|---|---|
| `1.0.0 - 2.0.0` | `1.2.3` / `2.2.3` | - | true / false |
| `0.1.20 \|\| 1.2.4` | `1.2.4` / `1.2.3` | - | true / false |
| `>=0.2.3 \|\| <0.0.1` | `0.0.0` / `0.0.3` | - | true / false |
| `1.2.x \|\| 2.x` | `2.1.3` / `3.1.3` | - | true / false |
| `\|\|` | `1.3.4` | - | true |
| `^1.2.3` | `1.2.3-pre` | - | false (prerelease rule) |
| `^1.2.3-alpha` | `1.2.3-pre` | - | true |
| `*` | `1.0.0-rc1` | `{includePrerelease: true}` | true |
| `>=0.1.97` | `v0.1.97` | loose | true |
| `<1` | `1.0.0beta` | loose | false |
| `*` | `undefined` | - | false |
| `*` | `'not a version'` | - | false |
| `>=2` | `'glorp'` | - | false |

## 5. Edge cases and constraints

- Must not modify the range; a passed `SemVer` is not modified either.
- Ranges may contain hundreds of `||` alternatives; the cost should be proportional to the sets examined.
