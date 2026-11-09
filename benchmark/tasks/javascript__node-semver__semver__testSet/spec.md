# Functional specification: `testSet(set, version, options)` in `semver.js`

## 1. Component overview

Module-private helper of node-semver. A range is a disjunction (`||`) of comparator sets; `testSet` decides whether
one version satisfies **one** comparator set (a conjunction). `Range.prototype.test` calls it for each set, so it is
behind `satisfies`, `maxSatisfying`, `minSatisfying`, `minVersion`, `gtr`/`ltr`, `intersects` and the CLI range
filter. Besides checking every comparator it applies npm's **prerelease rule**: a prerelease version only matches
when the range explicitly mentions a prerelease of the same `major.minor.patch`, unless prereleases are opted in.

## 2. Functional requirements

1. If any comparator of `set` rejects the version (`comparator.test(version)` is false), return `false`.
2. Otherwise, if the version has a prerelease (`version.prerelease.length > 0`) and `options.includePrerelease` is
   falsy:
   - return `true` if some comparator of the set, whose `semver` is not the `ANY` sentinel, has a version **with a
     prerelease** and the **same `major`, `minor` and `patch`** as `version` (the prerelease identifiers themselves
     need not be equal);
   - otherwise return `false`.
3. Otherwise return `true`.

## 3. Input specification

- `set`: array of `Comparator` objects (possibly a single comparator whose `semver` is `ANY`, i.e. "any version").
  Never empty when called from `Range`.
- `version`: a `SemVer` instance (callers convert strings beforehand).
- `options`: the normalised options object of the range (`{loose, includePrerelease}`); only `includePrerelease`
  matters here.

## 4. Output specification

A boolean. Examples (set written as range text, i.e. the comparators of `new Range(text).set[0]`):

| set | version | includePrerelease | result |
|---|---|---|---|
| `>=1.2.3-pre <=2.4.3-pre` (from `1.2.3-pre+asdf - 2.4.3-pre+asdf`) | `1.2.3-pre.2` | no | true |
| same | `2.4.3-alpha` | no | true |
| same | `1.2.3` | no | true |
| `>=1.2.3 <=2.4.3` (from `1.2.3+asdf - 2.4.3+asdf`) | `1.2.3-pre.2` | no | false |
| `>=1.2.3 <2.0.0` (`^1.2.3`) | `1.2.3-beta` | no | false |
| `>=1.2.3-alpha <2.0.0` (`^1.2.3-alpha`) | `1.2.3-pre` | no | true |
| same | `1.2.4-pre` | no | false |
| `<=1.2.3` | `1.2.3-beta` | no | false |
| `''` (ANY, from `*`) | `1.0.0-rc1` | no / yes | false / true |
| `>=1.0.0 <2.0.0` (`^1.0.0`) | `1.0.1-rc1` | yes | true |
| `>=1.0.0 <2.0.0` | `1.0.0-rc1` | yes | false (rejected by `>=1.0.0`) |
| `>=2.0.0-0 <3.0.0-0` (`2.x` with includePrerelease) | `2.0.0-pre.0` | yes | true |
| same | `3.0.0-pre.0` | yes | false |

## 5. Edge cases and constraints

- The prerelease rule is only applied after all comparators accepted the version.
- `ANY` comparators accept everything and never count as "mentioning a prerelease".
- Must not modify `set`, `version` or `options`.
- Sets can contain hundreds of comparators; the work is linear in the set length.
