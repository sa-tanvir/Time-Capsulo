You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func matchMapWithRegex(toCheck map[string]*regexp.Regexp, toMatch map[string][]string, canonicalKey bool) bool`

## 1. Component overview

`matchMapWithRegex` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). It decides whether every required key of a multi-valued
map (such as an `http.Header`) carries a value accepted by a regular
expression. The route matcher created by
`Route.HeadersRegexp("Content-Type", "application/(text|json)", ...)` compiles
each pattern and calls `matchMapWithRegex(required, req.Header, true)`.

## 2. Functional requirements

Return `true` if and only if **every** entry `(k, re)` of `toCheck` is
satisfied by `toMatch`:

1. **Key lookup.** If `canonicalKey` is `true`, the key looked up in `toMatch`
   is `http.CanonicalHeaderKey(k)` (e.g. `"foo"` → `"Foo"`,
   `"x-requested-with"` → `"X-Requested-With"`); otherwise `k` is used exactly
   as given. The keys of `toMatch` are never transformed.
2. **Key must exist.** If the looked-up key is absent from `toMatch`, or maps
   to a `nil` slice, the entry is not satisfied.
3. **`nil` regexp = presence only.** If `re` is `nil`, the entry is satisfied
   as soon as the key exists with a non-`nil` slice (even an empty one).
4. **Otherwise at least one value must match.** If `re` is not `nil`, the entry
   is satisfied only if `re.MatchString(value)` is `true` for at least one
   value in the slice. Matching is the standard unanchored `regexp` search: a
   pattern matches if it matches any substring, unless the pattern itself uses
   `^`/`$` anchors. An empty (non-`nil`) slice therefore fails for a non-`nil`
   regexp, even one compiled from `""`.

An empty (or `nil`) `toCheck` yields `true`. Extra keys in `toMatch` and extra
values are ignored.

Examples (`canonicalKey = true`; patterns shown as their source text):

| `toCheck` | `toMatch` | result |
|---|---|---|
| `{"Accept": "html"}` | `{"Accept": ["text/plain", "text/html"]}` | `true` |
| `{"Accept": "html"}` | `{"Accept": ["application/xhtml+xml"]}` | `true` (substring) |
| `{"Origin": "^https://example.co$"}` | `{"Origin": ["https://example.co"]}` | `true` |
| `{"Origin": "^https://example.co$"}` | `{"Origin": ["https://example.co.uk"]}` | `false` |
| `{"foo": "ba[zr]"}` | `{"Foo": ["baz"]}` | `true` |
| `{"foo": "ba[zr]"}` | `{"Foo": ["bat"]}` | `false` |
| `{"foo": ""}` | `{"Foo": ["anything"]}` | `true` |
| `{"foo": ""}` | `{"Foo": []}` | `false` |
| `{"foo": nil}` | `{"Foo": []}` | `true` |
| `{"foo": nil}` | `{}` | `false` |
| `{"foo": "x"}`, `canonicalKey = false` | `{"Foo": ["x"]}` | `false` |
| `{}` | anything | `true` |

## 3. Input specification

- `toCheck`: required keys with compiled patterns (`*regexp.Regexp`, possibly
  `nil`); may be `nil` or empty; up to a few hundred entries; keys in any case.
- `toMatch`: available values per key (typically an `http.Header`); may be
  `nil`; slices may hold dozens of values.
- `canonicalKey`: whether `toCheck` keys must be canonicalised as MIME header
  keys before lookup.

## 4. Output specification

- `bool` as described in section 2. The result does not depend on map
  iteration order.

## 5. Edge cases and constraints

- Neither map nor any regexp is modified.
- Only keys are canonicalised; values are passed to the regexp unchanged.
- Never panics for valid inputs; safe for concurrent use as long as the maps
  are not written concurrently (compiled regexps are safe to share).

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
matchMapWithString toCheck map [ string ] string , toMatch map [ string ] [ ] string , canonicalKey bool
methodNotAllowed w http . ResponseWriter , r * http . Request
methodNotAllowedHandler
setCurrentRoute r * http . Request , val interface { }
setVars r * http . Request , val interface { }
uniqueVars s1 , s2 [ ] string
```

## Notes

`http.CanonicalHeaderKey` (package `net/http`, imported in this file) returns
the canonical MIME header form of a key. The matcher type that uses this
function is:

```go
// headerRegexMatcher matches the request against the route given a regex for the header
type headerRegexMatcher map[string]*regexp.Regexp

func (m headerRegexMatcher) Match(r *http.Request, match *RouteMatch) bool {
	return matchMapWithRegex(m, r.Header, true)
}
```

=== STUB ===
```go
func matchMapWithRegex(toCheck map[string]*regexp.Regexp, toMatch map[string][]string, canonicalKey bool) bool {
    // TODO: implement according to the specification
}
```
