# Functional specification: `SemVer.prototype.comparePre(other)` in `semver.js`

## 1. Component overview

Method of the `SemVer` class of node-semver. It compares **only the prerelease parts** of two versions, following
the precedence rules of Semantic Versioning 2.0.0 §11. `SemVer.prototype.compare` uses it to break ties after the
`major.minor.patch` comparison, so every ordering helper of the library (`gt`, `lt`, `eq`, `cmp`, `sort`,
`satisfies`, `maxSatisfying`, `gtr`/`ltr`, ...) depends on it.

## 2. Functional requirements

1. If `other` is not a `SemVer` instance, it is first converted with `new SemVer(other, this.options)`; an invalid
   version therefore throws that constructor's `TypeError` (`'Invalid Version: ...'`).
2. The `major`, `minor`, `patch` and `build` fields of both versions are ignored.
3. A version **without** prerelease ranks **higher** than one with a prerelease:
   - this has a prerelease, other has none -> `-1`;
   - this has none, other has one -> `1`;
   - neither has one -> `0`.
4. Otherwise compare the two `prerelease` arrays identifier by identifier from the left:
   - identifiers that are strictly equal (`===`) are skipped;
   - at the first differing position the result is `compareIdentifiers(a, b)`: numeric identifiers compare
     numerically, a numeric identifier is lower than a non-numeric one, non-numeric identifiers compare in
     JavaScript string order (code units, so upper case sorts before lower case: `r100` > `R2`, and `r100` < `r2`);
   - if one array is a prefix of the other, the **shorter** one is lower (`a` < `a.b`);
   - if both run out together, the result is `0`.
5. The result is always one of the numbers `-1`, `0`, `1`.

## 3. Input specification

- `this`: a `SemVer` (fields `prerelease`, `options` used; see context).
- `other`: a `SemVer`, or a version string valid under `this.options` (strings are parsed as described above).
- Prerelease arrays may be long (hundreds of identifiers); identifiers are JS numbers or strings.

## 4. Output specification

`-1` if this prerelease has lower precedence than other's, `1` if higher, `0` if equal. Examples with
`p = new SemVer('1.2.3-alpha.0.pr.1')`:

| call | result |
|---|---|
| `p.comparePre('9.9.9-alpha.0.pr.1')` | `0` (main version ignored) |
| `p.comparePre('1.2.3')` | `-1` |
| `p.comparePre('1.2.3-alpha.0.pr.2')` | `-1` |
| `p.comparePre('1.2.3-alpha.0.2')` | `1` (`pr` > `2`) |
| `new SemVer('1.2.3-a.10').comparePre('1.2.3-a.5')` | `1` (numeric) |
| `new SemVer('1.2.3-a.b').comparePre('1.2.3-a')` | `1` (longer wins) |
| `new SemVer('1.2.3-5-foo').comparePre('1.2.3-5')` | `1` (`'5-foo'` is non-numeric) |
| `new SemVer('1.2.3').comparePre('2.0.0')` | `0` |

## 5. Edge cases and constraints

- Must not modify either version.
- Very large numeric-looking identifiers that were kept as strings (above `MAX_SAFE_INTEGER`) are still compared
  through `compareIdentifiers`.
- Pure apart from the possible construction of a SemVer from a string argument.
