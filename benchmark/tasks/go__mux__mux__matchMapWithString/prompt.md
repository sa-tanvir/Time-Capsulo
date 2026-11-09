You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `mux.go`

## Imports / includes available in this file

```
import "errors"
import "fmt"
import "net/http"
import "path"
import "regexp"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(r*Router)BuildVarsFunc f BuildVarsFunc
(r*Router)Get name string
(r*Router)GetRoute name string
(r*Router)Handle path string , handler http . Handler
(r*Router)HandleFunc path string , f func http . ResponseWriter , * http . Request
(r*Router)Headers pairs ... string
(r*Router)Host tpl string
(r*Router)Match req * http . Request , match * RouteMatch
(r*Router)MatcherFunc f MatcherFunc
(r*Router)Methods methods ... string
(r*Router)NewRoute
(r*Router)Path tpl string
(r*Router)PathPrefix tpl string
(r*Router)Queries pairs ... string
(r*Router)Schemes schemes ... string
(r*Router)ServeHTTP w http . ResponseWriter , req * http . Request
(r*Router)SkipClean value bool
(r*Router)StrictSlash value bool
(r*Router)UseEncodedPath
(r*Router)Walk walkFn WalkFunc
CurrentRoute r * http . Request
NewRouter
Vars r * http . Request
checkPairs pairs ... string
cleanPath p string
copyRouteConf r routeConf
copyRouteRegexp r * routeRegexp
mapFromPairsToRegex pairs ... string
mapFromPairsToString pairs ... string
matchInArray arr [ ] string , value string
matchMapWithRegex toCheck map [ string ] * regexp . Regexp , toMatch map [ string ] [ ] string , canonicalKey bool
methodNotAllowed w http . ResponseWriter , r * http . Request
methodNotAllowedHandler
setCurrentRoute r * http . Request , val interface { }
setVars r * http . Request , val interface { }
uniqueVars s1 , s2 [ ] string
```

## Notes

`http.CanonicalHeaderKey` (package `net/http`, imported in this file) returns
the canonical MIME header form of a key (`"x-requested-with"` →
`"X-Requested-With"`). The header matcher type that uses this function is:

```go
// headerMatcher matches the request against header values.
type headerMatcher map[string]string

func (m headerMatcher) Match(r *http.Request, match *RouteMatch) bool {
	return matchMapWithString(m, r.Header, true)
}
```

=== STUB ===
```go
func matchMapWithString(toCheck map[string]string, toMatch map[string][]string, canonicalKey bool) bool {
    // TODO: implement according to the specification
}
```
