You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `semver.js`

## Imports / includes available in this file

```
(none)
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( _ , M , m , p , pr )
(anonymous) ( a , b )
(anonymous) ( c )
(anonymous) ( comp )
(anonymous) ( comparator )
(anonymous) ( comps )
(anonymous) ( id )
(anonymous) ( otherComparator )
(anonymous) ( range )
(anonymous) ( rangeComparator )
(anonymous) ( rangeComparators )
(anonymous) ( ret , gtlt , M , m , p , pr )
(anonymous) ( thisComparator )
(anonymous) ( thisComparators )
(anonymous) ( v )
Comparator ( comp , options )
Comparator.prototype.intersects ( comp , options )
Comparator.prototype.parse ( comp )
Comparator.prototype.test ( version )
Comparator.prototype.toString ( )
Range ( range , options )
Range.prototype.format ( )
Range.prototype.intersects ( range , options )
Range.prototype.parseRange ( range )
Range.prototype.toString ( )
SemVer ( version , options )
SemVer.prototype.compare ( other )
SemVer.prototype.compareBuild ( other )
SemVer.prototype.compareMain ( other )
SemVer.prototype.comparePre ( other )
SemVer.prototype.format ( )
SemVer.prototype.inc ( release , identifier )
SemVer.prototype.toString ( )
clean ( version , options )
cmp ( a , op , b , loose )
coerce ( version , options )
compare ( a , b , loose )
compareBuild ( a , b , loose )
compareIdentifiers ( a , b )
compareLoose ( a , b )
debug ( )
diff ( version1 , version2 )
eq ( a , b , loose )
gt ( a , b , loose )
gte ( a , b , loose )
gtr ( version , range , options )
hyphenReplace ( $0 , from , fM , fm , fp , fpr , fb , to , tM , tm , tp , tpr , tb )
inc ( version , release , loose , identifier )
intersects ( r1 , r2 , options )
isSatisfiable ( comparators , options )
isX ( id )
lt ( a , b , loose )
lte ( a , b , loose )
ltr ( version , range , options )
major ( a , loose )
maxSatisfying ( versions , range , options )
minSatisfying ( versions , range , options )
minVersion ( range , loose )
minor ( a , loose )
neq ( a , b , loose )
outside ( version , range , hilo , options )
parse ( version , options )
parseComparator ( comp , options )
patch ( a , loose )
prerelease ( version , options )
rcompare ( a , b , loose )
rcompareIdentifiers ( a , b )
replaceCaret ( comp , options )
replaceCarets ( comp , options )
replaceStars ( comp , options )
replaceTilde ( comp , options )
replaceTildes ( comp , options )
replaceXRange ( comp , options )
replaceXRanges ( comp , options )
rsort ( list , loose )
satisfies ( version , range , options )
sort ( list , loose )
testSet ( set , version , options )
toComparators ( range , options )
tok ( n )
valid ( version , options )
validRange ( range , options )
```

## Variables declared at the same scope level (you may use them)

```
var MAX_LENGTH = 256
var MAX_SAFE_INTEGER = Number.MAX_SAFE_INTEGER ||
  /* istanbul ignore next */ 9007199254740991

// Max safe segment length for coercion.
var MAX_SAFE_COMPONENT_LENGTH = 16

// The actual regexps go on exports.re
var re = exports.re = []
var src = exports.src = []
var t = exports.tokens = {}
var R = 0

function tok (n) {
  t[n] = R++
}

// The following Regular Expressions can be used for tokenizing,
// validating, and parsing SemVer version strings.

// ## Numeric Identifier
// A single `0`, or a non-zero digit followed by zero or more digits.

tok('NUMERICIDENTIFIER')
src[t.NUMERICIDENTIFIER] = '0|[1-9]\\d*'
    ...
var tildeTrimReplace = '$1~'

tok('TILDE')
src[t.TILDE] = '^' + src[t.LONETILDE] + src[t.XRANGEPLAIN] + '$'
tok('TILDELOOSE')
src[t.TILDELOOSE] = '^' + src[t.LONETILDE] + src[t.XRANGEPLAINLOOSE] + '$'

// Caret ranges.
// Meaning is "at least and backwards compatible with"
tok('LONECARET')
src[t.LONECARET] = '(?:\\^)'

tok('CARETTRIM')
src[t.CARETTRIM] = '(\\s*)' + src[t.LONECARET] + '\\s+'
re[t.CARETTRIM] = new RegExp(src[t.CARETTRIM], 'g')
var caretTrimReplace = '$1^'

tok('CARET')
src[t.CARET] = '^' + src[t.LONECARET] + src[t.XRANGEPLAIN] + '$'
tok('CARETLOOSE')
src[t.CARETLOOSE] = '^' + src[t.LONECARET] + src[t.XRANGEPLAINLOOSE] + '$'

// A simple gt/lt/eq thing, or just "" to indicate "any version"
tok('COMPARATORLOOSE')
src[t.COMPARATORLOOSE] = '^' + src[t.GTLT] + '\\s*(' + src[t.LOOSEPLAIN] + ')$|^$'
    ...
var comparatorTrimReplace = '$1$2$3'

// Something like `1.2.3 - 1.2.4`
// Note that these all use the loose form, because they'll be
// checked against either the strict or loose comparator form
// later.
tok('HYPHENRANGE')
src[t.HYPHENRANGE] = '^\\s*(' + src[t.XRANGEPLAIN] + ')' +
                   '\\s+-\\s+' +
                   '(' + src[t.XRANGEPLAIN] + ')' +
                   '\\s*$'

tok('HYPHENRANGELOOSE')
src[t.HYPHENRANGELOOSE] = '^\\s*(' + src[t.XRANGEPLAINLOOSE] + ')' +
                        '\\s+-\\s+' +
                        '(' + src[t.XRANGEPLAINLOOSE] + ')' +
                        '\\s*$'

// Star ranges basically just allow anything at all.
tok('STAR')
src[t.STAR] = '(<|>)?=?\\s*\\*'

// Compile to actual regexp objects.
// All are flag-free, unless they were created above with a flag.
for (var i = 0; i < R; i++) {
    ...
var numeric = /^[0-9]+$/
function compareIdentifiers (a, b) {
  var anum = numeric.test(a)
  var bnum = numeric.test(b)

  if (anum && bnum) {
    a = +a
    b = +b
  }

  return a === b ? 0
    : (anum && !bnum) ? -1
    : (bnum && !anum) ? 1
    : a < b ? -1
    : 1
}

exports.rcompareIdentifiers = rcompareIdentifiers
function rcompareIdentifiers (a, b) {
  return compareIdentifiers(b, a)
}

exports.major = major
function major (a, loose) {
  return new SemVer(a, loose).major
    ...
var ANY = {}
Comparator.prototype.parse = function (comp) {
  var r = this.options.loose ? re[t.COMPARATORLOOSE] : re[t.COMPARATOR]
  var m = comp.match(r)

  if (!m) {
    throw new TypeError('Invalid comparator: ' + comp)
  }

  this.operator = m[1] !== undefined ? m[1] : ''
  if (this.operator === '=') {
    this.operator = ''
  }

  // if it literally is just '>' or '' then allow anything.
  if (!m[2]) {
    this.semver = ANY
  } else {
    this.semver = new SemVer(m[2], this.options.loose)
  }
}

Comparator.prototype.toString = function () {
  return this.value
}
    ...
```

## Instance state: `SemVer` objects

`new SemVer(version, options)` (also callable without `new`) parses a version string; `options` is normalised to an
object `{loose, includePrerelease}` (a non-object value `x` becomes `{loose: !!x, includePrerelease: false}`). It
throws `TypeError('Invalid Version: ' + version)` on invalid input. Passing a SemVer whose `loose` flag equals the
requested one returns that same object. Fields of an instance:

| field | type | meaning |
|---|---|---|
| `options` | object | the normalised options |
| `loose` | boolean | loose parsing mode |
| `raw` | string | the string the object was built from |
| `major`, `minor`, `patch` | number | numeric components |
| `prerelease` | array | prerelease identifiers; identifiers made only of digits are stored as JS numbers (when below `MAX_SAFE_INTEGER`), all others as strings. `[]` when there is none |
| `build` | array of strings | build-metadata identifiers (`'1.0.0+1.0'` -> `['1', '0']`), `[]` when none |
| `version` | string | canonical `major.minor.patch[-prerelease]` (no build metadata) |

Methods: `format()` recomputes `version` from the numeric fields and `prerelease` and returns it; `toString()`
returns `version`; `compare(other)`, `compareMain(other)`, `comparePre(other)`, `compareBuild(other)` return
-1/0/1; `inc(release, identifier)`.

Module-level helper `compareIdentifiers(a, b)`: if both are made only of digits they are compared numerically;
a numeric identifier sorts before a non-numeric one; otherwise compared with `<` (code-unit order). Returns -1/0/1.

## Instance state: `Range` objects

| field | type | meaning |
|---|---|---|
| `options` | object | normalised options `{loose, includePrerelease}` |
| `loose` | boolean | `!!options.loose` |
| `includePrerelease` | boolean | `!!options.includePrerelease` |
| `raw` | string | the range string given to the constructor |
| `set` | array of arrays of Comparator | disjunction (`||`) of conjunctions: a version satisfies the range when it satisfies every comparator of at least one inner array |
| `range` | string | canonical form, computed by `format()` |

Methods: `format()` sets and returns `range` (comparators of a set joined by one space, sets joined by `'||'`, each
part trimmed); `toString()` returns `range`; `parseRange(str)` turns one `||`-free part into an array of
Comparators; `test(version)`; `intersects(range, options)`.

Module-level helper `testSet(set, version, options)`: `set` is one array of Comparators, `version` a `SemVer`.
Returns `true` when every comparator accepts the version and, if the version has a prerelease and
`options.includePrerelease` is falsy, some non-`ANY` comparator of the set has a prerelease version with the same
`major.minor.patch` (npm's prerelease rule); `false` otherwise.

=== STUB ===
```javascript
Range.prototype.test = function (version) {
    // TODO: implement according to the specification
}
```
