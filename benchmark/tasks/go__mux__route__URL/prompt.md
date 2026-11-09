You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *Route) URL(pairs ...string) (*url.URL, error)`

## 1. Component overview

`URL` belongs to the `mux` package (`github.com/gorilla/mux`, an HTTP request
router). It performs **reverse routing**: given values for the route's
variables, it builds the URL that the route would match. Example:

```go
r := mux.NewRouter()
r.Host("{subdomain}.domain.com").
  Path("/articles/{category}/{id:[0-9]+}").
  Name("article")
u, err := r.Get("article").URL("subdomain", "news", "category", "technology", "id", "42")
// u.String() == "http://news.domain.com/articles/technology/42", err == nil
```

A route may have a host template (`r.regexp.host`), a path or path-prefix
template (`r.regexp.path`), and any number of query templates
(`r.regexp.queries`), each a `*routeRegexp` able to fill in its own variables
with `url(values)` (see context).

## 2. Functional requirements

1. **Route error.** If `r.err` is non-nil, return `nil` and `r.err` itself.
2. **Variables.** Turn `pairs` (`name, value, name, value, ...`) into the
   variable map using `r.prepareVars(pairs...)` (which also applies the
   route's `BuildVarsFunc`, if any). If that fails (odd number of strings),
   return `nil` and its error unchanged (message
   `mux: number of parameters must be multiple of 2, got [x]` for `URL("x")`).
3. **Host.** If the route has a host template, build the host with its
   `url(values)`; on error return `nil` and that error. When a host exists,
   the scheme is the route's `buildScheme` if non-empty, else `"http"`.
   Without a host template, the scheme stays empty even if `Schemes(...)` was
   called.
4. **Path.** If the route has a path (or path-prefix) template, build the path
   with its `url(values)`; on error return `nil` and that error.
5. **Queries.** For each query template, in registration order, build its
   `key=value` part with `url(values)`; on the first error return `nil` and
   that error. Join the parts with `&` to form the raw query (empty when there
   are no query templates).
6. **Order of failures.** Host is built first, then path, then queries; the
   first failing part's error is returned.
7. **Result.** On success return a new `*url.URL` with exactly these fields set:
   `Scheme`, `Host`, `Path`, `RawQuery` (all others zero). Extra names in
   `pairs` are ignored.

Examples (`u.String()` shown):

| route | pairs | result |
|---|---|---|
| `Host("foo.domain.com")` | none | `http://foo.domain.com` |
| `Host("{subdomain}.domain.com")` | subdomain=bar | `http://bar.domain.com` |
| `Host("foo.domain.com").Path("/articles")` | none | `http://foo.domain.com/articles` |
| `Path("/articles/{category}/{id:[0-9]+}")` | category=technology, id=42 | `/articles/technology/42` |
| `Schemes("https", "ftp").Host("localhost")` | none | `https://localhost` |
| `Path("/a").Schemes("https")` | none | `/a` (no host → no scheme) |
| `Host("www.example.com").Path("/api").Queries("foo", "bar", "baz", "ding")` | none | `http://www.example.com/api?foo=bar&baz=ding` |
| `Queries("foo", "{v1}", "bar", "", "baz", "lit")` | v1=`a b` | `?foo=a+b&bar=&baz=lit` (RawQuery `foo=a+b&bar=&baz=lit`) |
| `Path("/a/{x}")` | x=1, x=2 | `/a/2` |
| `PathPrefix("/static/")` | none | `/static/` |
| route with no templates | none | `""` (empty URL) |

Errors (`nil` URL): `Host("{h}.com").Queries("foo", "{v1:[0-9]+}")` with
v1=1 → `mux: missing route variable "h"`; `Path("/articles/{category}/{id:[0-9]+}")`
with id=x → `mux: variable "x" doesn't match, expected "^[0-9]+$"`;
`Host("{h}.com").Path("/{p:[0-9]+}")` with h=x, p=y →
`mux: variable "y" doesn't match, expected "^[0-9]+$"`.

## 3. Input specification

- `r`: a route built with the fluent API (possibly via subrouters, whose
  routes inherit the parent's host/path templates and scheme). Routes can have
  up to a few hundred variables over host, path and queries.
- `pairs`: an even (or, erroneously, odd) number of strings.

## 4. Output specification

- `(*url.URL, nil)` on success, `(nil, error)` on failure, with errors passed
  through unchanged from `r.err`, `prepareVars` or the templates' `url`.

## 5. Edge cases and constraints

- The route is not modified; `pairs` is not modified.
- Path and host values are inserted verbatim; query values are escaped by the
  query templates.
- Safe for concurrent use if the route's `BuildVarsFunc` is.

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
(r*Route)Match req * http . Request , match * RouteMatch
(r*Route)MatcherFunc f MatcherFunc
(r*Route)Methods methods ... string
(r*Route)Name name string
(r*Route)Path tpl string
(r*Route)PathPrefix tpl string
(r*Route)Queries pairs ... string
(r*Route)Schemes schemes ... string
(r*Route)SkipClean
(r*Route)Subrouter
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

## Helper contracts

```go
// prepareVars converts the route variable pairs ("name1", "value1", "name2",
// "value2", ...) into a map (a later duplicate name overwrites an earlier one).
// If the number of strings is odd it returns nil and the error
//   mux: number of parameters must be multiple of 2, got [<pairs>]
// (the pairs slice formatted with %v). If the route has a BuildVarsFunc, the
// map is passed through it and its result is returned.
func (r *Route) prepareVars(pairs ...string) (map[string]string, error)
```

`Schemes(...)` stores the first scheme (lower-cased) in `buildScheme`.

=== STUB ===
```go
func (r *Route) URL(pairs ...string) (*url.URL, error) {
    // TODO: implement according to the specification
}
```
