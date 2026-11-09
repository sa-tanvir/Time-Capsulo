You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `coerce(version, options)` in `semver.js`

## 1. Component overview

Public helper `semver.coerce` of node-semver. It extracts something that looks like a version number
(`major[.minor[.patch]]`) from arbitrary text and turns it into a `SemVer`, filling missing minor/patch with `0`
and dropping everything else (prerelease tags, build metadata, surrounding text). Used e.g. by
`semver -c [--rtl]` on the command line.

## 2. Functional requirements

1. If `version` is already a `SemVer` instance, return it unchanged (same object).
2. If `version` is a number, convert it with `String(version)` (`10` -> `'10'`, `1.5` -> `'1.5'`).
3. Any other non-string (`null`, objects, functions, booleans, `undefined`) -> return `null`.
4. `options` defaults to `{}` when falsy. Only `options.rtl` is interpreted here; the whole `options` value is
   passed on to `parse` (so `options.loose` is honoured there).
5. **Coercible match.** A coercible match is a run of 1–16 decimal digits that is at the start of the string or
   preceded by a non-digit (the major), optionally followed by `.` + 1–16 digits (minor), optionally followed by
   `.` + 1–16 digits (patch), such that the match is at the end of the string or followed by a non-digit; the
   longest such form is taken (`M.m.p`, else `M.m`, else `M`). Digit runs of 17+ digits can never form a component,
   and a component is dropped if the next character is a digit:
   `'1.' + '2'x17 + '.3'` -> `1.0.0`; `'1'x17 + '.2.3'` -> `2.3.0`; `'1.2.' + '3'x17` -> `1.2.0`.
6. **Default mode** (`options.rtl` falsy): use the left-most coercible match.
7. **Right-to-left mode** (`options.rtl` truthy): pick the right-most coercible match that does not share its end
   with a match further left. Precisely: enumerate, left to right, the coercible matches whose major starts at
   each digit run (start of string or preceded by a non-digit) - this includes runs that are minor or patch
   components of an earlier match. The *end* of a match counts the one non-digit delimiter after it, when present.
   Keep a current choice: each enumerated match replaces it unless both have the same end. Stop as soon as the
   current choice ends at the end of the string. Examples: `'1.2.3.4'` -> `2.3.4`; `'1.2.3.4.5.6'` -> `4.5.6`;
   `'1.2.3/a/b/c/2.3.4'` -> `2.3.4`; `'1.2.3.4.5/6'`, `'1.2.3.4./6'`, `'1.2.3/6'` -> `6.0.0`;
   `'1.2.3.4xyz'` -> `2.3.4`; `'a1.2b3.4c'` -> `3.4.0`.
8. If there is no coercible match, return `null`.
9. Otherwise return `parse(major + '.' + (minor || '0') + '.' + (patch || '0'), options)` - the digit strings are used
   as written. Consequently the result is `null` when a component is too large for a safe integer
   (`'9999999999999999'` -> `null`) or, in strict mode, has a leading zero (`'01.2.3'` -> `null`, but
   `coerce('01.2.3', {loose: true})` -> `1.2.3`).
10. Calling the function must not leave any shared state that affects later results: repeated calls with the same
    arguments give the same result, in either mode and in any order. The only module state involved is
    `re[t.COERCERTL].lastIndex` (a global RegExp). An rtl call must scan from the start of the string whatever
    `lastIndex` holds on entry, and when an rtl call returns (match or not), `re[t.COERCERTL].lastIndex` is `-1`
    (which `exec` treats like `0`). Default-mode calls do not touch it (`re[t.COERCE]` is not global).

## 3. Input specification

- `version`: any value; meaningful inputs are strings (any length, any characters), numbers and SemVer objects.
- `options`: `undefined`/falsy, or an object with optional boolean `rtl` and optional `loose`/`includePrerelease`
  (forwarded to `parse`).

## 4. Output specification

A `SemVer` (whose `version` is `major.minor.patch`, never with prerelease or build) or `null`.

| input | result `.version` |
|---|---|
| `null`, `{version: '1.2.3'}`, a function, `''`, `'.'`, `'version one'` | `null` |
| `'9'x16`, `'1'x17`, `'a' + '1'x17`, `'1'x17 + 'a'`, `'9'x16 + '.4.7.4'` | `null` |
| `'.1'`, `'.1.'`, `'..1'`, `'1.'`, `'1'`, `' 1'`, `'1 0'`, `'v1'`, `'a1a'`, `'version1'` | `1.0.0` |
| `'.1.1'`, `'1.1-1'`, `'1.1 1'`, `'version1.1'` | `1.1.0` |
| `'1.2.3.4'`, `'v1.2.3.4'` | `1.2.3` |
| `'42.6.7.9.3-alpha'` | `42.6.7` |
| `'v3.4 replaces v3.3.1'` | `3.4.0` |
| `'11' + '.1'x126` | `11.1.1` |
| `'1.2.3.' + '4'x1024` | `1.2.3` |
| `'1'x17 + '.4.7.4'` | `4.7.4` |
| `10` | `10.0.0` |
| `semver.parse('1.2.3')` | the same object |

## 5. Edge cases and constraints

- Never throws for any input.
- Prerelease/build text after the numbers is ignored (`'v1.2.3-beta+x'` -> `1.2.3`).
- The returned SemVer's `raw` is the assembled `M.m.p` string.
- Inputs can be long (thousands of characters); the work should stay roughly linear in the input length.

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
SemVer.prototype.inc ( release , identifier )
SemVer.prototype.toString ( )
clean ( version , options )
cmp ( a , op , b , loose )
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

`parse(version, options)` (public, same file) returns a `SemVer` for a valid version string, the argument itself
when it is already a SemVer, and `null` for anything invalid (it never throws). In strict mode (the default)
numeric components with leading zeros (`01`) are invalid; components above `MAX_SAFE_INTEGER` are invalid.

=== STUB ===
```javascript
function coerce (version, options) {
    // TODO: implement according to the specification
}
```
