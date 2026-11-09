You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *Router) Match(req *http.Request, match *RouteMatch) bool`

## 1. Component overview

`(*Router).Match` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). It attempts to match a request against the router's
registered routes (and, through them, its subrouters). If a route matches, the
`Route`, `Handler` and `Vars` fields of `match` are filled and it returns
`true`. If no route matches, it returns `false` and records the reason in
`match.MatchErr`; if a handler is registered for that failure type
(`NotFoundHandler`, `MethodNotAllowedHandler`), that handler is put in
`match.Handler` and `true` is returned instead. `ServeHTTP` calls it and then
runs `match.Handler`; subrouters are matched by calling their `Match` from the
parent route.

## 2. Functional requirements

1. **Routes in registration order.** Call `route.Match(req, match)` for each
   route in `r.routes`, in order, passing the same `match`. Stop at the first
   route that returns `true`.
2. **Middleware on success.** When a route matched and `match.MatchErr` is
   `nil`, wrap `match.Handler` with the router's middlewares so that the
   middleware added **first** with `Use` is the **outermost** one: apply them
   from the last to the first, each time replacing `match.Handler` with
   `mw.Middleware(match.Handler)`. With middlewares `mw0, mw1` and route
   handler `h`, the final handler behaves as `mw0(mw1(h))`. When a route
   matched but `match.MatchErr` is non-nil (e.g. a subrouter answered with its
   own not-found handler and left `ErrNotFound`), the handler is **not**
   wrapped. In both cases return `true`.
3. **Method not allowed.** If no route matched and `match.MatchErr` is
   `ErrMethodMismatch` (some route matched everything except the method): if
   `r.MethodNotAllowedHandler` is non-nil, set `match.Handler` to it and
   return `true` (`MatchErr` stays `ErrMethodMismatch`); otherwise return
   `false` (with `MatchErr` still `ErrMethodMismatch`, `Handler` unchanged).
4. **Not found.** Otherwise, set `match.MatchErr = ErrNotFound`. If
   `r.NotFoundHandler` is non-nil, also set `match.Handler` to it and return
   `true`; else return `false`.
5. Middlewares are never applied to the not-found or method-not-allowed
   handlers.

Examples:

| router | request | result |
|---|---|---|
| `Path("/products/")` named `stock` | `GET http://www.example.com/products/` | `true`, `Route` = that route, `MatchErr = nil` |
| same | `GET .../products` | `false`, `MatchErr = ErrNotFound`, `Handler = nil` |
| `Host("www.example.com").Subrouter()` with child `Path("/products/")` | `GET http://www.example.com/products/` | `true`, `Route` = the child route |
| `HandleFunc("/", h).Methods("GET","POST")` | `PUT /` | `false`, `MatchErr = ErrMethodMismatch` |
| plus a second route `HandleFunc("/", h2).Methods("PUT")` | `PUT /` | `true`, `MatchErr = nil`, `Handler` = `h2` (wrapped by middlewares) |
| `Methods("GET")` route, `MethodNotAllowedHandler = h405`, `NotFoundHandler = h404`, one middleware | `POST /` | `true`, `Handler = h405` (unwrapped), `MatchErr = ErrMethodMismatch` |
| same | `GET /x` (no route) | `true`, `Handler = h404`, `MatchErr = ErrNotFound` |
| `HandleFunc("/", h)`, `PathPrefix("/sub/").Subrouter()` with child `HandleFunc("/", h)` | `GET /sub/whatever` | `false`, `MatchErr = ErrNotFound` |
| same, subrouter has `NotFoundHandler = s404` | `GET /sub/whatever` | `true`, `Handler = s404`, `MatchErr = ErrNotFound`, no middleware applied |
| no routes, `NotFoundHandler = h404` | anything | `true`, `Handler = h404`, `MatchErr = ErrNotFound` |
| strict-slash route `Path("/111/")`, middlewares `mw0, mw1` | `GET /111` | `true`, `Handler` = `mw0(mw1(redirect to /111/))` |

## 3. Input specification

- `r`: a router with zero or more routes (possibly hundreds, possibly with
  subrouters), zero or more middlewares, and optional `NotFoundHandler` /
  `MethodNotAllowedHandler`.
- `req`: an `*http.Request` with non-nil `URL` and `Header`.
- `match`: non-nil; usually zero-valued (when called for a subrouter it holds
  the state of the parent's matching so far).

## 4. Output specification

- `bool` as described; `match` updated (`Route`, `Handler`, `Vars` by the
  matching route; `Handler` possibly wrapped by middlewares or set to a
  failure handler; `MatchErr` as described).

## 5. Edge cases and constraints

- The router, its routes and the request are not modified.
- Middleware functions are invoked (to build the chain) once per successful
  match; the resulting handler is not executed by `Match`.
- Safe for concurrent use with distinct `match` values, provided the
  middleware functions are.

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
matchMapWithString toCheck map [ string ] string , toMatch map [ string ] [ ] string , canonicalKey bool
methodNotAllowed w http . ResponseWriter , r * http . Request
methodNotAllowedHandler
setCurrentRoute r * http . Request , val interface { }
setVars r * http . Request , val interface { }
uniqueVars s1 , s2 [ ] string
```

## Package-level types and variables used by this method

```go
var (
	// ErrMethodMismatch is returned when the method in the request does not match
	// the method defined against the route.
	ErrMethodMismatch = errors.New("method is not allowed")
	// ErrNotFound is returned when no route match is found.
	ErrNotFound = errors.New("no matching route was found")
)

// Router registers routes to be matched and dispatches a handler.
type Router struct {
	// Configurable Handler to be used when no route matches.
	NotFoundHandler http.Handler
	// Configurable Handler to be used when the request method does not match the route.
	MethodNotAllowedHandler http.Handler
	// Routes to be matched, in order.
	routes []*Route
	// Routes by name for URL building.
	namedRoutes map[string]*Route
	// Deprecated, no effect.
	KeepContext bool
	// Slice of middlewares to be called after a match is found, in the order
	// they were added with Use(...).
	middlewares []middleware
	// configuration shared with `Route`
	routeConf
}

// RouteMatch stores information about a matched route.
type RouteMatch struct {
	Route   *Route
	Handler http.Handler
	Vars    map[string]string
	// MatchErr is set to appropriate matching error
	// It is set to ErrMethodMismatch if there is a mismatch in
	// the request method and route method
	MatchErr error
}

// middleware interface is anything which implements a MiddlewareFunc named Middleware.
type middleware interface {
	Middleware(handler http.Handler) http.Handler
}
```

## Helper contract: `(*Route).Match(req, match) bool` (route.go)

Tries one route. Returns `true` and fills `match` (`Route` if nil, `Handler`
if nil, `Vars`) when all of the route's matchers accept the request. When only
the route's method matcher(s) failed it returns `false` and sets
`match.MatchErr = ErrMethodMismatch`. When another matcher fails it returns
`false` and resets a `MatchErr` of `ErrNotFound` to `nil`. When it matches
while `match.MatchErr == ErrMethodMismatch`, it clears `MatchErr` and replaces
`match.Handler` with its own handler. A route may contain a subrouter (a
`*Router` used as matcher), whose `Match` is this very method; it may leave
`MatchErr = ErrNotFound` together with a returned `true` when the subrouter
has its own `NotFoundHandler`.

=== STUB ===
```go
func (r *Router) Match(req *http.Request, match *RouteMatch) bool {
    // TODO: implement according to the specification
}
```
