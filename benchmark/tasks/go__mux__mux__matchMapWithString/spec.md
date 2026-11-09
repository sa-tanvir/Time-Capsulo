# Functional specification: `func matchMapWithString(toCheck map[string]string, toMatch map[string][]string, canonicalKey bool) bool`

## 1. Component overview

`matchMapWithString` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). It decides whether a set of required key/value pairs is
present in a multi-valued map such as an `http.Header`. The route matcher
created by `Route.Headers("Content-Type", "application/json", ...)` calls it as
`matchMapWithString(required, req.Header, true)`, so a route only matches a
request whose headers contain every required pair.

## 2. Functional requirements

Return `true` if and only if **every** entry `(k, v)` of `toCheck` is satisfied
by `toMatch`:

1. **Key lookup.** If `canonicalKey` is `true`, the key looked up in `toMatch`
   is `http.CanonicalHeaderKey(k)` (e.g. `"x-requested-with"` →
   `"X-Requested-With"`); otherwise `k` is used exactly as given. The keys of
   `toMatch` are never transformed.
2. **Key must exist.** If the looked-up key is absent from `toMatch`, or maps
   to a `nil` slice, the entry is not satisfied.
3. **Empty required value = presence only.** If `v` is `""`, the entry is
   satisfied as soon as the key exists with a non-`nil` slice (even an empty,
   non-`nil` slice).
4. **Otherwise exact membership.** If `v` is not empty, the entry is satisfied
   only if at least one string in the slice is exactly equal to `v`
   (case-sensitive, no trimming, no pattern matching: `"ba[zr]"` does not match
   `"bar"`).

An empty (or `nil`) `toCheck` yields `true`. Extra keys in `toMatch` and extra
values in a slice are ignored.

Examples (`canonicalKey = true` unless noted):

| `toCheck` | `toMatch` | result |
|---|---|---|
| `{"x-requested-with": "XMLHttpRequest"}` | `{"X-Requested-With": ["XMLHttpRequest"]}` | `true` |
| `{"x-requested-with": ""}` | `{"X-Requested-With": ["anything"]}` | `true` |
| `{"x-requested-with": "XMLHttpRequest"}` | `{}` | `false` |
| `{"x-requested-with": "a"}`, `canonicalKey = false` | `{"X-Requested-With": ["a"]}` | `false` |
| `{"foo": "bar", "baz": "ding"}`, `false` | `{"foo": ["bar"], "baz": ["dong"]}` | `false` |
| `{"foo": "bar", "baz": "ding"}`, `false` | `{"foo": ["x", "bar"], "baz": ["ding"]}` | `true` |
| `{"k": ""}` | `{"K": []}` (non-nil, empty) | `true` |
| `{}` | anything | `true` |

## 3. Input specification

- `toCheck`: required pairs; may be `nil` or empty; keys may be in any letter
  case; values may be `""`. Up to a few hundred entries.
- `toMatch`: the available values per key (typically an `http.Header`, whose
  keys are already canonical). May be `nil`. Slices may hold dozens of values.
- `canonicalKey`: whether the `toCheck` keys must be canonicalised as MIME
  header keys before lookup.

## 4. Output specification

- `bool` as described in section 2. The result does not depend on map
  iteration order.

## 5. Edge cases and constraints

- Neither map is modified.
- Value comparison is exact; only keys are canonicalised (and only when
  `canonicalKey` is set).
- Pure function apart from reading the maps; never panics; safe for concurrent
  use as long as the maps are not being written concurrently.
