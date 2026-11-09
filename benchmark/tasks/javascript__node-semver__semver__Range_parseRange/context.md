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
Range.prototype.test ( version )
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

## Instance state: `Comparator` objects

| field | type | meaning |
|---|---|---|
| `options` | object | normalised options `{loose, includePrerelease}` |
| `loose` | boolean | `!!options.loose` |
| `operator` | string | one of `''` (equality), `'<'`, `'<='`, `'>'`, `'>='` |
| `semver` | SemVer or `ANY` | the version operand; the module-level sentinel object `ANY` (`var ANY = {}`) means "matches every version" |
| `value` | string | `operator + semver.version`, or `''` when `semver` is `ANY` |

`Comparator.prototype.parse(comp)` matches `comp` against `re[t.COMPARATORLOOSE]` / `re[t.COMPARATOR]` (by
`this.options.loose`), sets `this.operator` (`'='` is stored as `''`) and `this.semver` (`ANY` when the version
part is empty, otherwise `new SemVer(versionPart, this.options.loose)`), and throws
`TypeError('Invalid comparator: ' + comp)` when it does not match. `test(version)` returns whether a version
(string or SemVer) satisfies the comparator (always `true` for `ANY`; invalid version strings give `false`).
`toString()` returns `value`.

## Regular expressions (module level)

`re` is an array of compiled RegExps indexed through the token table `t` (`re[t.NAME]`); `src[t.NAME]` holds the
source text. The ones relevant here:

| token | matches |
|---|---|
| `t.FULL` / `t.LOOSE` | a whole strict / loose version |
| `t.COMPARATOR` / `t.COMPARATORLOOSE` | `^<op>\s*<version>$` or the empty string; group 1 = operator (`''`, `<`, `<=`, `>`, `>=`, `=`), group 2 = version |
| `t.HYPHENRANGE` / `t.HYPHENRANGELOOSE` | a whole `X - Y` range (anchored); the replacement function `hyphenReplace` rewrites such a match to the equivalent comparators (`1.2 - 3.4.5` -> `>=1.2.0 <=3.4.5`) |
| `t.COMPARATORTRIM` (global) | an operator followed by whitespace and a version; with the replacement pattern `comparatorTrimReplace` that whitespace is removed (`'> 1.2.3'` -> `'>1.2.3'`) |
| `t.TILDETRIM` (global) | `~` / `~>` followed by whitespace; the replacement pattern `tildeTrimReplace` removes the whitespace |
| `t.CARETTRIM` (global) | `^` followed by whitespace; the replacement pattern `caretTrimReplace` removes the whitespace |
| `t.COERCE` | `(^|[^\d])(\d{1,16})(?:\.(\d{1,16}))?(?:\.(\d{1,16}))?(?:$|[^\d])` - group 2/3/4 = major/minor/patch |
| `t.COERCERTL` | the same pattern with the global flag (its `lastIndex` is shared module state) |

Module-level helper `parseComparator(comp, options)` desugars one space-free range token - carets, tildes, x-ranges and stars - into plain comparator text, e.g. `'^1.2.3'` -> `'>=1.2.3 <2.0.0'`,
`'1.2.x'` -> `'>=1.2.0 <1.3.0'`, `'*'` / `'x'` -> `''`, `'>*'` -> `'<0.0.0-0'`; plain comparators pass through.
`MAX_SAFE_COMPONENT_LENGTH = 16`.
