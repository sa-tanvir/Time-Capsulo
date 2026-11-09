# Functional specification: `Range.prototype.parseRange(range)` in `semver.js`

## 1. Component overview

Method of the `Range` class of node-semver. The `Range` constructor splits a range string on `||` and calls this
method for each part; it turns one `||`-free part (a conjunction such as `'>= 1.2.7 <1.3.0'`, `'~1.2'`,
`'1.2 - 3.4.5'`, `'^1.2.3 1.x'`) into an array of plain `Comparator` objects. All of npm's range sugar - hyphen
ranges, tildes, carets, x-ranges, stars, partial versions - is resolved here (with the helpers listed in the
context).

## 2. Functional requirements

Parsing mode comes from `this.options` (`loose`, `includePrerelease`). Steps, in order:

1. Trim the input.
2. **Hyphen range.** If the whole (trimmed) part is `A - B` (two partial versions separated by whitespace, `-`,
   whitespace; loose or strict partial-version grammar by mode), replace it by its comparators as `hyphenReplace`
   does: `1.2 - 3.4.5` -> `>=1.2.0 <=3.4.5`, `1.2.3 - 3.4` -> `>=1.2.3 <3.5.0`, `1.2.3 - 3` -> `>=1.2.3 <4.0.0`,
   `x - 1.0.0` -> `<=1.0.0`, `1.2.3 - x` -> `>=1.2.3`, `1.2.3-pre+asdf - 2.4.3-pre+asdf` -> `>=1.2.3-pre <=2.4.3-pre`.
3. **Remove whitespace after operators**: between `<`, `<=`, `>`, `>=`, `=` and the following version
   (`'>=  1.0.0'` -> `'>=1.0.0'`, `'<\t2'` -> `'<2'`), after `~` / `~>` (`'~> 1'` -> `'~>1'`) and after `^`.
4. Collapse every run of whitespace to one space; the part is now a list of space-separated tokens.
5. Desugar each token with `parseComparator(token, this.options)` (carets, tildes, x-ranges, stars; e.g.
   `^1.2.3` -> `>=1.2.3 <2.0.0`, `~1.2` -> `>=1.2.0 <1.3.0`, `1.2.x` -> `>=1.2.0 <1.3.0`, `>1.2` -> `>=1.3.0`,
   `<=7.x` -> `<8.0.0`, `*`/`x` -> `''`, `>*` -> `<0.0.0-0`, `2.x` with includePrerelease -> `>=2.0.0-0 <3.0.0-0`).
   Join the results with single spaces and split the result on runs of whitespace. Consequently an empty
   desugared token in the middle disappears, while one at the very start or end yields an empty comparator string
   (`'1.2.3 *'` -> `['1.2.3', '']`, `'* 1.2.3'` -> `['', '1.2.3']`, `'1.2.3 * 2.0.0'` -> `['1.2.3', '2.0.0']`;
   `'*'` and `''` -> `['']`).
6. **Loose mode only:** discard every comparator string that does not match the loose comparator grammar
   (`re[t.COMPARATORLOOSE]`; the empty string matches) - invalid tokens are silently dropped.
7. Build `new Comparator(str, this.options)` for each remaining string, in order, and return the array. In strict
   mode an invalid token makes this throw `TypeError('Invalid comparator: <token>')` (for example `'1 - 2 3'`
   is not a hyphen range, so the token `-` is invalid).

## 3. Input specification

- `this`: a `Range` (only `this.options` is read; no field is written).
- `range`: string without `||`; may be empty, padded with spaces/tabs, and may contain hundreds of tokens.

## 4. Output specification

Array of `Comparator` objects (never empty in strict mode; possibly empty in loose mode). Values of the
comparators for some inputs:

| input | options | values |
|---|---|---|
| `'1.0.0 - 2.0.0'` | - | `>=1.0.0`, `<=2.0.0` |
| `'>= 1.0.0   <\t2'` | - | `>=1.0.0`, `<2.0.0` |
| `'~ 1.0.3'`, `'~> 1.0.3'` | - | `>=1.0.3`, `<1.1.0` |
| `'^ 1.2 ^ 1'` | - | `>=1.2.0`, `<2.0.0`, `>=1.0.0`, `<2.0.0` |
| `'1 2'` | - | `>=1.0.0`, `<2.0.0`, `>=2.0.0`, `<3.0.0` |
| `'> 1 < 3'` | - | `>=2.0.0`, `<3.0.0` |
| `'^0.0.1-beta'` | - | `>=0.0.1-beta`, `<0.0.2` |
| `'>*'`, `'<*'` | - | `<0.0.0-0` |
| `'>=1.2.3 garbage'` | loose | `>=1.2.3` |
| `'>=1.2.3 garbage'` | strict | throws `TypeError('Invalid comparator: garbage')` |
| `'~1.2.3beta'` | loose | `>=1.2.3-beta`, `<1.3.0` |
| `'1.2.3pre+asdf - 2.4.3pre+asdf'` | loose | `>=1.2.3-pre`, `<=2.4.3-pre` |
| `'>01.02.03'` | loose / strict | `>1.2.3` / throws `TypeError` |

## 5. Edge cases and constraints

- Must not modify `this`; it may be called on any Range instance with the desired options.
- The hyphen form is recognised only when it spans the whole part.
- Work should be linear in the number of tokens.
