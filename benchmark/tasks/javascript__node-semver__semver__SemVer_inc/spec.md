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
