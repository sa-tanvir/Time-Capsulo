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
