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
