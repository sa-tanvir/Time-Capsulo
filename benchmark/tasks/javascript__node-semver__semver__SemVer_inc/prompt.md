You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `SemVer.prototype.inc(release, identifier)` in `semver.js`

## 1. Component overview

Method of the `SemVer` class of node-semver (the semantic-version library used by npm). It bumps the version held
by the receiver **in place** according to a release type, and returns the receiver. It backs the public
`semver.inc(version, release, loose, identifier)` helper (which returns the new version string, or `null` when this
method throws) and the CLI `semver -i <release> [--preid=<id>]`.

## 2. Functional requirements

Let "has a prerelease" mean `this.prerelease.length > 0`. Behaviour by `release`:

1. **`'major'`**: if minor is not 0, or patch is not 0, or there is no prerelease, increment `major`; in every case
   set minor and patch to 0 and clear the prerelease. (`1.2.3` -> `2.0.0`; `1.2.3-4` -> `2.0.0`; but a pre-major
   version `1.0.0-1` -> `1.0.0`.)
2. **`'minor'`**: if patch is not 0 or there is no prerelease, increment `minor`; set patch to 0 and clear the
   prerelease. (`1.2.3` -> `1.3.0`; `1.2.0-1` -> `1.2.0`; `1.2.3-4` -> `1.3.0`.)
3. **`'patch'`**: if there is no prerelease, increment `patch`; clear the prerelease. (`1.2.3` -> `1.2.4`;
   `1.2.0-0` -> `1.2.0`; `1.2.3-alpha.0.beta` -> `1.2.3`.)
4. **`'pre'`** (low-level step, also used by the other `pre*` types):
   - with no prerelease, the prerelease becomes `[0]`;
   - otherwise, the **right-most identifier that is a number** (`typeof` is `'number'`; a string identifier is never
     incremented, even when it is made of digits, e.g. one kept as a string because it was too large to store as a
     safe integer) is incremented by one; if no identifier is a number, `0` is appended (`beta` -> `beta.0`, `alpha.10.beta` -> `alpha.11.beta`,
     `alpha.10.beta.2` -> `alpha.10.beta.3`, `alpha.10.1.beta` -> `alpha.10.2.beta`).
   - then, if `identifier` is truthy: when the first prerelease identifier equals `identifier` (strict equality),
     the prerelease is kept unless its second element is "not a number" in the sense of the global `isNaN` (which
     converts its argument: a missing element or a non-numeric string such as `'bar'` is not a number, while a
     numeric string such as `'99999999999999999'` counts as a number and is kept), in which case it becomes
     `[identifier, 0]`; when the first identifier differs, the prerelease becomes `[identifier, 0]`.
     (`1.2.3-alpha.0` with `'alpha'` -> `1.2.3-alpha.1`; with `'dev'` -> `1.2.3-dev.0`;
     `1.2.3-dev.bar` with `'dev'` -> `1.2.3-dev.0`.)
5. **`'prerelease'`**: if there is no prerelease, first apply `'patch'`; then apply `'pre'` (with `identifier`).
   (`1.2.4` -> `1.2.5-0`; `1.2.3-0` -> `1.2.3-1`; `1.2.3-alpha.9.beta` -> `1.2.3-alpha.10.beta`;
   `1.2.4` with `'dev'` -> `1.2.5-dev.0`.)
6. **`'prepatch'`**: clear the prerelease, apply `'patch'` (so patch is incremented), then `'pre'`.
   (`1.2.0` and `1.2.0-1` -> `1.2.1-0`; with `'dev'` -> `1.2.1-dev.0`.)
7. **`'preminor'`**: clear the prerelease, set patch to 0, increment minor, then `'pre'`.
   (`1.2.0` and `1.2.3-1` -> `1.3.0-0`.)
8. **`'premajor'`**: clear the prerelease, set minor and patch to 0, increment major, then `'pre'`.
   (`1.2.0` and `1.2.3-1` -> `2.0.0-0`; with `'dev'` -> `2.0.0-dev.0`.)
9. **Anything else** (e.g. `'fake'`, `''`, `undefined`): throw `new Error('invalid increment argument: ' + release)`
   (an `Error`, not a `TypeError`); the receiver is not modified in that case.
10. After a successful bump: recompute `version` with `this.format()`, set `this.raw` to that new `version`, and
    return `this`.

`identifier` is only used by the `pre*`/`prerelease` types; it is ignored by `major`, `minor` and `patch`.

## 3. Input specification

- `this`: a valid `SemVer` (see context: `major`, `minor`, `patch` numbers, `prerelease` array of numbers/strings,
  `build`, `version`, `raw`).
- `release`: string, one of the types above (any other value is an error).
- `identifier`: optional string (prerelease tag such as `'alpha'`, `'dev'`), or `undefined`/falsy.

## 4. Output specification

Returns the receiver (`this`), mutated: `major`, `minor`, `patch`, `prerelease`, `version` and `raw` updated as
described. `build` is left untouched (and is not part of `version`). Examples (receiver -> new `version`):

| receiver | release | identifier | result |
|---|---|---|---|
| `1.2.3` | `major` / `minor` / `patch` | - | `2.0.0` / `1.3.0` / `1.2.4` |
| `1.2.3-tag` | `major` | - | `2.0.0` |
| `1.0.0-1` | `major` | `'dev'` | `1.0.0` |
| `1.2.3-alpha.0.beta` | `prerelease` | - | `1.2.3-alpha.1.beta` |
| `1.2.3-alpha.0.beta` | `prerelease` | `'alpha'` | `1.2.3-alpha.1.beta` |
| `1.2.3-alpha.10.0.beta` | `prerelease` | `'dev'` | `1.2.3-dev.0` |
| `1.2.3` | `fake` | - | throws `Error` |

## 5. Edge cases and constraints

- Numeric prerelease identifiers are JS numbers; incrementing keeps them numbers, so `format()` prints them
  normally (`alpha.9` -> `alpha.10`).
- `raw` must equal the new `version` after the call (the original input text is not kept).
- The method must be callable repeatedly on the same object (each call bumps again).
- No other global state is used.

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
Range.prototype.test ( version )
Range.prototype.toString ( )
SemVer ( version , options )
SemVer.prototype.compare ( other )
SemVer.prototype.compareBuild ( other )
SemVer.prototype.compareMain ( other )
SemVer.prototype.comparePre ( other )
SemVer.prototype.format ( )
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

=== STUB ===
```javascript
SemVer.prototype.inc = function (release, identifier) {
    // TODO: implement according to the specification
}
```
