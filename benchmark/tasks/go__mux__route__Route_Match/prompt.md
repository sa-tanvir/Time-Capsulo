You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *Route) Match(req *http.Request, match *RouteMatch) bool`

## 1. Component overview

`(*Route).Match` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). A route is a list of matchers (host/path/query
templates, methods, headers, schemes, custom functions, subrouters) added with
the fluent builder API. `(*Router).Match` calls `route.Match(req, &match)` for
each registered route in turn until one returns `true`; the same
`RouteMatch` value is passed to every route, so its `MatchErr` carries
information between routes (e.g. "some route matched everything except the
HTTP method", which lets the router answer 405 instead of 404). On success the
match receives the route, its handler and the route variables.

## 2. Functional requirements

1. **Unusable routes.** If the route is build-only (`r.buildOnly`) or has a
   build error (`r.err != nil`), return `false` without touching `match`.
2. **Run every matcher in order.** Call `m.Match(req, match)` for each
   matcher `m` in `r.matchers`:
   - If a matcher of type `methodMatcher` fails, remember a method mismatch
     and **continue** with the next matchers.
   - If any other matcher fails: if `match.MatchErr` is currently
     `ErrNotFound` (left there, e.g., by a subrouter that found nothing), reset
     it to `nil`; forget any remembered method mismatch; return `false`
     immediately. (Any other `MatchErr` value, including `ErrMethodMismatch`
     set earlier, is left as is.)
3. **Only the method failed.** If all non-method matchers succeeded but a
   method matcher failed, set `match.MatchErr = ErrMethodMismatch` and return
   `false` (no other field is changed).
4. **Full match.** Otherwise the route matches:
   1. If `match.MatchErr` is `ErrMethodMismatch` (an earlier route matched
      everything but the method), set `match.MatchErr = nil` and set
      `match.Handler = r.handler`, overriding any handler already there.
      Any other `MatchErr` value (e.g. `ErrNotFound`) is left unchanged.
   2. If `match.Route` is `nil`, set it to `r` (a route already set — e.g. by
      a subrouter matcher — is kept).
   3. If `match.Handler` is `nil`, set it to `r.handler`.
   4. If `match.Vars` is `nil`, set it to a new empty map.
   5. Call `setMatch` on the route's template group (`r.regexp`), passing the request, the match and the route itself, to add the route variables (and
      a possible strict-slash redirect handler).
   6. Return `true`.

Examples:

| route | request / initial match | result |
|---|---|---|
| `Methods("GET","POST")` | `PUT`, empty match | `false`, `MatchErr = ErrMethodMismatch` |
| `Methods("GET").Path("/a")` | `PUT /b`, empty | `false`, `MatchErr = nil` |
| `Methods("GET").Path("/a")` | `PUT /b`, `MatchErr = ErrNotFound` | `false`, `MatchErr = nil` |
| `Methods("GET").Path("/a")` | `PUT /b`, `MatchErr = ErrMethodMismatch` | `false`, still `ErrMethodMismatch` |
| `Path("/a")` | `GET /a`, `MatchErr = ErrMethodMismatch`, `Handler = h0` | `true`, `MatchErr = nil`, `Handler = r.handler`, `Route = r`, `Vars = {}` |
| `Path("/a")` | `GET /a`, `MatchErr = ErrNotFound` | `true`, `MatchErr` stays `ErrNotFound`, `Route = r` |
| `Path("/{v}")` | `GET /a`, `Route = r0`, `Handler = h0`, `Vars = {pre: x}` | `true`, `Route = r0`, `Handler = h0`, `Vars = {pre: x, v: a}` |
| `Host("{v1}.google.com").Path("/{var2:[a-z]+}/{var3:[0-9]+}").Queries("foo","bar").Methods("GET").Schemes("https").Headers("x-requested-with","XMLHttpRequest")` | `GET https://www.google.com/product/42?foo=bar` with that header | `true`, `Vars = {v1: www, var2: product, var3: 42}` |
| same | `POST`, header present | `false`, `ErrMethodMismatch` |
| same | `POST`, header missing | `false`, `MatchErr = nil` |
| `Path("/111/")` with strict slash | `GET /111` | `true`, `Handler` = redirect to `/111/` |
| `PathPrefix("/sub").Subrouter()` + child `Path("/x/{c0}")` | `GET /sub/x/1` | `true`, `Route` = the child route, `Vars = {c0: 1}` |
| route with no matchers | anything | `true` |
| build-only or erroneous route | anything | `false`, match untouched |

## 3. Input specification

- `r`: a route built with the fluent API; up to a few hundred matchers /
  variables.
- `req`: an `*http.Request` with non-nil `URL` and `Header`.
- `match`: non-nil; may be zero-valued or carry state left by earlier routes
  (`MatchErr`, `Route`, `Handler`, `Vars`).

## 4. Output specification

- `bool`: whether the route matched; `match` updated as described.

## 5. Edge cases and constraints

- `r` and `req` are never modified.
- When `false` is returned, `Route`, `Handler` and `Vars` are not set by this
  route itself (a subrouter matcher may have written to them).
- Safe for concurrent use with distinct `match` values.

=== CONTEXT ===
# Context for the function to implement

- **Language:** go
- **File:** `route.go`

## Imports / includes available in this file

```
import "errors"
import "fmt"
import "net/http"
import "net/url"
import "regexp"
import "strings"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(m headerMatcher)Match r * http . Request , match * RouteMatch
(m headerRegexMatcher)Match r * http . Request , match * RouteMatch
(m methodMatcher)Match r * http . Request , match * RouteMatch
(m schemeMatcher)Match r * http . Request , match * RouteMatch
(r*Route)BuildOnly
(r*Route)GetError
(r*Route)GetHandler
(r*Route)GetHostTemplate
(r*Route)GetMethods
(r*Route)GetName
(r*Route)GetPathRegexp
(r*Route)GetPathTemplate
(r*Route)GetQueriesRegexp
(r*Route)GetQueriesTemplates
(r*Route)Handler handler http . Handler
(r*Route)HandlerFunc f func http . ResponseWriter , * http . Request
(r*Route)Headers pairs ... string
(r*Route)HeadersRegexp pairs ... string
(r*Route)Host tpl string
(r*Route)MatcherFunc f MatcherFunc
(r*Route)Methods methods ... string
(r*Route)Name name string
(r*Route)Path tpl string
(r*Route)PathPrefix tpl string
(r*Route)Queries pairs ... string
(r*Route)Schemes schemes ... string
(r*Route)SkipClean
(r*Route)Subrouter
(r*Route)URL pairs ... string
(r*Route)URLHost pairs ... string
(r*Route)URLPath pairs ... string
(r*Route)addMatcher m matcher
(r*Route)addRegexpMatcher tpl string , typ regexpType
(r*Route)buildVars m map [ string ] string
(r*Route)prepareVars pairs ... string
```

## Package-level types (`route.go`, `mux.go`, `regexp.go`)

```go
// Route stores information to match a request and build URLs.
type Route struct {
	handler     http.Handler      // request handler for the route
	buildOnly   bool              // if true, this route never matches: it is only used to build URLs
	name        string            // the name used to build URLs
	err         error             // error resulted from building a route
	namedRoutes map[string]*Route // "global" reference to all named routes
	routeConf                     // config possibly passed in from `Router`
}

// common route configuration shared between `Router` and `Route`
type routeConf struct {
	useEncodedPath bool             // match against the escaped path ("/path/foo%2Fbar/to")
	strictSlash    bool             // "/path/" vs "/path" redirect behaviour
	skipClean      bool
	regexp         routeRegexpGroup // the host, path and query templates of the route
	matchers       []matcher        // list of matchers, in the order they were added
	buildScheme    string           // the scheme used when building URLs ("" = none set)
	buildVarsFunc  BuildVarsFunc
}

// routeRegexpGroup groups the route matchers that carry variables.
type routeRegexpGroup struct {
	host    *routeRegexp   // nil if the route has no host template
	path    *routeRegexp   // nil if the route has no path / path-prefix template
	queries []*routeRegexp // one per Queries key/value pair, in order
}

// matcher types try to match a request.
type matcher interface {
	Match(*http.Request, *RouteMatch) bool
}

// BuildVarsFunc may modify route variables before a route's URL is built.
type BuildVarsFunc func(map[string]string) map[string]string

// RouteMatch stores information about a matched route.
type RouteMatch struct {
	Route    *Route
	Handler  http.Handler
	Vars     map[string]string
	MatchErr error // ErrMethodMismatch / ErrNotFound, see mux.go
}
```

A `*routeRegexp` (see `regexp.go`) is the compiled form of one template; its
fields include `template string` (the template as given, e.g.
`"/articles/{category}/{id:[0-9]+}"` or `"foo={v1}"`), `regexp
*regexp.Regexp` (the whole-template regexp), and `varsN []string` (variable
names in order). It implements `matcher`, and has
`url(values map[string]string) (string, error)`, which substitutes the values
into the template (query values are query-escaped) and returns errors
`mux: missing route variable "<name>"` or
`mux: variable "<value>" doesn't match, expected "<pattern>"`.

## More package-level declarations used by this method

```go
var (
	// ErrMethodMismatch is returned when the method in the request does not match
	// the method defined against the route.
	ErrMethodMismatch = errors.New("method is not allowed")
	// ErrNotFound is returned when no route match is found.
	ErrNotFound = errors.New("no matching route was found")
)

// methodMatcher matches the request against HTTP methods (added by Methods(...)).
type methodMatcher []string

func (m methodMatcher) Match(r *http.Request, match *RouteMatch) bool {
	return matchInArray(m, r.Method)
}
```

Other matcher kinds stored in `r.matchers` (in the order the builder methods
were called): `*routeRegexp` (host / path / path prefix / one per query pair),
`headerMatcher`, `headerRegexMatcher`, `schemeMatcher`, `MatcherFunc`, and
`*Router` (added by `Subrouter()`; its `Match` tries the subrouter's routes,
fills `Route`/`Handler`/`Vars` of the match on success, and on failure may set
`MatchErr` to `ErrNotFound` or `ErrMethodMismatch`).

## Helper contract

```go
// setMatch (regexp.go) adds the route variables found in the request's host,
// path and query string to m.Vars (which must be non-nil) and, for
// strict-slash path templates whose trailing slash differs from the
// request's, replaces m.Handler with a 301 redirect handler.
func (v routeRegexpGroup) setMatch(req *http.Request, m *RouteMatch, r *Route)
```

=== STUB ===
```go
func (r *Route) Match(req *http.Request, match *RouteMatch) bool {
    // TODO: implement according to the specification
}
```
