# Context for the function to implement

- **Language:** go
- **File:** `regexp.go`

## Imports / includes available in this file

```
import "bytes"
import "fmt"
import "net/http"
import "net/url"
import "regexp"
import "strconv"
import "strings"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(r*routeRegexp)Match req * http . Request , match * RouteMatch
(r*routeRegexp)getURLQuery req * http . Request
(r*routeRegexp)matchQueryString req * http . Request
(r*routeRegexp)url values map [ string ] string
braceIndices s string
extractVars input string , matches [ ] int , names [ ] string , output map [ string ] string
getHost r * http . Request
newRouteRegexp tpl string , typ regexpType , options routeRegexpOptions
varGroupName idx int
```

## Package-level types and constants (`regexp.go`)

```go
type routeRegexpOptions struct {
	strictSlash    bool
	useEncodedPath bool
}

type regexpType int

const (
	regexpTypePath   regexpType = 0
	regexpTypeHost   regexpType = 1
	regexpTypePrefix regexpType = 2
	regexpTypeQuery  regexpType = 3
)

// routeRegexp stores a regexp to match a host or path and information to
// collect and validate route variables.
type routeRegexp struct {
	template   string           // the unmodified template
	regexpType regexpType       // the type of match
	options    routeRegexpOptions
	regexp     *regexp.Regexp   // expanded regexp
	reverse    string           // reverse template
	varsN      []string         // variable names
	varsR      []*regexp.Regexp // variable regexps (validators)
}
```

## Instance state of `routeRegexp` (built by `newRouteRegexp`)

| field | meaning |
|---|---|
| `template` | the template exactly as given, e.g. `"/articles/{category}/{id:[0-9]+}"`, `"{sub}.domain.com"`, `"foo={v1}"` (query templates are always `key=value`) |
| `regexpType` | path, host, path prefix or query |
| `options.strictSlash` | only ever `true` for path templates (forced `false` for the other types) |
| `options.useEncodedPath` | match against the escaped request path |
| `regexp` | the whole template as one anchored regexp. Variables become named groups `v0`, `v1`, ... in order of appearance; literal text is quoted. Default variable pattern: `[^/]+` (path/prefix), `[^.]+` (host), `.*` (query). With strict slash a trailing `/` is optional (`[/]?`); prefix templates have no `$` anchor; a query template with an empty value (`"foo="`) matches any value. Examples: `"/articles/{category}/{id:[0-9]+}"` → `^/articles/(?P<v0>[^/]+)/(?P<v1>[0-9]+)$`; `"{v1:[a-z]+}.google.com"` → `^(?P<v0>[a-z]+)\.google\.com$`; `"foo={v1}"` → `^foo=(?P<v0>.*)$`; `"/111/"` with strict slash → `^/111[/]?$`; prefix `"/static/"` → `^/static/` |
| `reverse` | a `fmt` format string with one `%s` per variable in place of the `{...}` tokens, literal text kept (a trailing `/` removed and re-added under strict slash, so it equals the template's shape): `"/articles/%s/%s"`, `"%s.google.com"`, `"foo=%s"`, `"/111/"`. Templates never contain `%` |
| `varsN` | variable names in order of appearance (`["category", "id"]`) |
| `varsR` | per variable, its own pattern compiled as `^pattern$` (`varsR[1].String() == "^[0-9]+$"`; default patterns likewise, e.g. `"^[^/]+$"`) |

## Related types (`route.go`, `mux.go`)

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


## Helper contracts (`regexp.go`)

```go
// getHost returns the request host: req.URL.Host if req.URL is absolute
// (has a scheme), otherwise req.Host (which may include a port).
func getHost(r *http.Request) string

// extractVars stores, for every i, output[names[i]] = the text of capture
// group i+1 of input, given the index pairs returned by
// (*regexp.Regexp).FindStringSubmatchIndex(input).
func extractVars(input string, matches []int, names []string, output map[string]string)

// getURLQuery returns "key=value" for a query template "key=...": the first
// (decoded) value of that key in req.URL's query, or "" if the key is absent
// or r is not a query template.
func (r *routeRegexp) getURLQuery(req *http.Request) string
```
