# Functional specification: `SemVer.prototype.compareBuild(other)` in `semver.js`

## 1. Component overview

Method of the `SemVer` class of node-semver. It compares **only the build-metadata parts** (`+...`) of two versions.
The public helper `semver.compareBuild(a, b)` uses it as a tie-breaker after the normal precedence comparison, so
that `semver.sort` / `semver.rsort` give a deterministic order to versions that differ only in build metadata
(`1.2.3` < `1.2.3+0` < `1.2.3+1`).

## 2. Functional requirements

1. If `other` is not a `SemVer` instance, it is first converted with `new SemVer(other, this.options)`; an invalid
   version therefore throws that constructor's `TypeError`.
2. Only the `build` arrays are compared; `major`, `minor`, `patch` and `prerelease` are ignored.
3. Compare the two `build` arrays identifier by identifier from the left:
   - identifiers that are strictly equal (`===`) are skipped;
   - at the first differing position the result is `compareIdentifiers(a, b)` (identifiers made only of digits
     compare numerically - so `'10'` > `'9'` and `'001'` equals `'1'` numerically - a numeric identifier is lower
     than a non-numeric one, other identifiers compare in JavaScript string order);
   - if one array runs out first, that version is **lower** (no build < any build; `+0` < `+0.0`; `+1.0` > `+1`);
   - if both run out together, the result is `0` (two versions without build metadata compare equal).
4. The result is one of `-1`, `0`, `1`.

## 3. Input specification

- `this`: a `SemVer` (fields `build`, `options` used; `build` is an array of strings).
- `other`: a `SemVer`, or a version string valid under `this.options`.
- Build arrays may be long (hundreds of identifiers).

## 4. Output specification

| receiver | other | result |
|---|---|---|
| `1.0.0` | `1.0.0+0` | `-1` |
| `1.0.0+0` | `1.0.0+0` | `0` |
| `1.0.0+0` | `1.0.0` | `1` |
| `1.0.0+0` | `'1.0.0+0.0'` | `-1` |
| `1.0.0+0` | `1.0.0+1` | `-1` |
| `1.0.0+1` | `1.0.0+0` | `1` |
| `1.0.0+1.0` | `1.0.0+1` | `1` |
| `1.2.3+10` | `1.2.3+9` | `1` |
| `1.2.3+a` | `1.2.3+1` | `1` |
| `9.9.9+x` | `0.0.1+x` | `0` |

## 5. Edge cases and constraints

- Must not modify either version.
- Note that numerically equal but textually different identifiers (`'001'` vs `'1'`) are not `===`, so they reach
  `compareIdentifiers`, which reports them as equal (`0`) - and that `0` is the result of the whole comparison.
- No other state is read or written.
