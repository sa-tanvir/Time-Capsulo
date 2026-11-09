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
