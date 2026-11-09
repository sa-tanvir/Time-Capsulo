# Functional specification: `outside(version, range, hilo, options)` in `semver.js`

## 1. Component overview

Public helper `semver.outside` of node-semver. It tells whether a version lies entirely **above** (`hilo === '>'`)
or entirely **below** (`hilo === '<'`) every version the range can match. The public helpers
`gtr(version, range, options)` and `ltr(version, range, options)` are thin wrappers calling it with `'>'` and
`'<'`.

## 2. Functional requirements

1. Convert the arguments, in this order: `version = new SemVer(version, options)`, then
   `range = new Range(range, options)`. Invalid input therefore throws the constructors' `TypeError`
   (`'Invalid Version: ...'`, `'Invalid SemVer Range: ...'`, `'Invalid comparator: ...'`).
2. Then validate `hilo`: anything other than `'>'` or `'<'` throws
   `new TypeError('Must provide a hilo val of "<" or ">"')` (exact message).
3. If the version satisfies the range (`satisfies(version, range, options)`), return `false`.
4. Otherwise examine every comparator set (`range.set`, the `||` alternatives). Inside a set, comparators whose
   `semver` is `ANY` are treated as `new Comparator('>=0.0.0')`. Version comparisons use SemVer precedence (build
   metadata ignored).

   **For `hilo === '>'`** - let *H* be the comparator of the set with the highest version and *L* the one with the
   lowest version (on ties, the earliest comparator in the set). Return `false` immediately if any of these holds:
   - *H*'s operator is `'>'` or `'>='` (the set is unbounded above);
   - *L*'s operator is `''` (equality) or `'>'`, and `version <= L.semver`;
   - *L*'s operator is `'>='` and `version < L.semver`.

   **For `hilo === '<'`** - the mirror image: *H* is the comparator with the **lowest** version and *L* the one
   with the **highest** version (ties: earliest). Return `false` if:
   - *H*'s operator is `'<'` or `'<='` (unbounded below);
   - *L*'s operator is `''` or `'<'`, and `version >= L.semver`;
   - *L*'s operator is `'<='` and `version > L.semver`.
5. If no set triggered a `false`, return `true`.

## 3. Input specification

- `version`: a version string or `SemVer`.
- `range`: a range string (`'1.2.x || >=2.5.0'`, `'~1.2.2'`, `'1.0.0 - 2.0.0'`, ...), a `Range` or a `Comparator`.
- `hilo`: `'>'` or `'<'` (anything else is an error).
- `options`: `undefined`, a boolean (`loose`) or an object `{loose, includePrerelease}`; forwarded to the
  constructors and to `satisfies`.

## 4. Output specification

A boolean. Examples (`gtr` = `outside(v, r, '>')`, `ltr` = `outside(v, r, '<')`):

| range | version | `>` | `<` |
|---|---|---|---|
| `~1.2.2` | `1.3.0` | true | false |
| `1.0.0 - 2.0.0` | `2.0.1` / `0.9.9` | true / false | false / true |
| `1.0.0` | `1.0.1-beta1` | true | false |
| `<2.0.0` | `2.0.0` | true | false |
| `0.1.20 \|\| 1.2.4` | `1.2.5` | true | false |
| `=0.7.x` | `0.8.0-asdf` | true | true |
| `1` (loose) | `2.0.0beta` | true | true |
| `>=1.0.0` | `1.1.0` | false | false |
| `*` | `v1.2.3-foo` | false | true |
| `~0.6.1-1` | `0.6.1-1` | false | false |
| `^0.1.0 \|\| ~3.0.1 \|\| 5.0.0` | `3.2.0` | false | false |
| `^0.1.0 \|\| ~3.0.1 \|\| >4 <=5.0.0` | `3.5.0` | false | false |
| `=0.1.0` | `1.0.0` | true | false |
| `<=1.2.3` | `1.2.3-beta` | true | false |

`outside('1.2.3', '>1.5.0', 'blerg', true)` throws `TypeError('Must provide a hilo val of "<" or ">"')`.

## 5. Edge cases and constraints

- A version that fails only because of its prerelease tag (e.g. `1.2.3-beta` against `<=1.2.3`) is judged by the
  comparator rules of step 4, not by the prerelease rule; this is why a prerelease
  version can be reported as outside in both directions (`=0.7.x` / `0.8.0-asdf` above).
- Must not modify the range or version passed in (a passed `SemVer`/`Range` may be reused by the conversion).
- Ranges may contain hundreds of comparators; the work should be linear in their number.
