You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *Route) Queries(pairs ...string) *Route`

## 1. Component overview

`Queries` belongs to the `mux` package (`github.com/gorilla/mux`, an HTTP
request router). It is part of the fluent route-building API: it adds matchers
for URL query parameters to the route and returns the route so calls can be
chained, e.g.

```go
r := mux.NewRouter()
r.Path("/api").Queries("foo", "bar", "id", "{id:[0-9]+}")
```

This route only matches requests whose URL contains `foo=bar` and an `id`
parameter made of digits (e.g. `?foo=bar&id=42`); `id` becomes a route
variable. Errors are not returned directly: like every builder method, they
are recorded in the route's `err` field (visible through `GetError()`), after
which the route never matches.

## 2. Functional requirements

1. **Arguments are key/value pairs.** `pairs` is read as
   `key1, value1, key2, value2, ...`.
2. **Odd count.** If the number of strings is odd, set `r.err` to an error with
   message `mux: number of parameters must be multiple of 2, got <pairs>`,
   where `<pairs>` is the slice formatted with `%v` (e.g.
   `mux: number of parameters must be multiple of 2, got [foo bar baz]`),
   add no matcher, and return **`nil`** (not the route). This happens even
   if the route already had an error.
3. **One query template per pair.** Otherwise, for each pair in order, build
   the template `key + "=" + value` and register it on the route as a
   query-type template (`regexpTypeQuery`) via `addRegexpMatcher` (see context).
   The result of each registration is stored in `r.err` (so a successful
   registration leaves `r.err == nil`). As soon as one registration yields an
   error, stop: later pairs are not registered (pairs registered before it
   stay registered), and return `r`.
4. **Existing error.** If the route already has an error, the registration
   helper reports that same error; `r.err` keeps it, nothing is added, and `r`
   is returned.
5. **Return value.** In all non-odd cases return the receiver `r`. With zero
   arguments nothing changes and `r` is returned.

Resulting templates (as reported by `GetQueriesTemplates()`) and regexps (as
reported by `GetQueriesRegexp()`):

| call | templates | regexps |
|---|---|---|
| `Queries("foo", "bar", "baz", "ding")` | `foo=bar`, `baz=ding` | `^foo=bar$`, `^baz=ding$` |
| `Queries("foo", "{v1}")` | `foo={v1}` | `^foo=(?P<v0>.*)$` |
| `Queries("foo", "{v1:[0-9]+}")` | `foo={v1:[0-9]+}` | `^foo=(?P<v0>[0-9]+)$` |
| `Queries("foo", "{v-1}", "baz", "{v-2}")` | `foo={v-1}`, `baz={v-2}` | `^foo=(?P<v0>.*)$`, `^baz=(?P<v0>.*)$` |
| `Queries("foo", "")` | `foo=` | `^foo=.*$` (any value, key must be present) |

Errors: `Queries("foo", "{v1}", "bar", "{v1}", "baz", "x")` registers only
`foo={v1}` and sets `mux: duplicated route variable "v1"`; on a route with
`Host("{v1}.example.com")`, `Queries("foo", "{v1}")` sets the same error;
`Queries("foo", "{bar", "baz", "1")` sets `mux: unbalanced braces in "foo={bar"`
and registers nothing.

## 3. Input specification

- `r`: a route (possibly with host, path or earlier query templates, possibly
  already carrying an error).
- `pairs`: zero or more strings; keys are plain parameter names, values are
  literal text, `""`, or contain `{name}` / `{name:pattern}` variables. Up to a
  few hundred pairs.

## 4. Output specification

- Returns `r`, or `nil` for an odd number of arguments.
- Side effects on `r`: `r.err` as described; on success one query
  `*routeRegexp` per pair appended (in order) to `r.regexp.queries` and to
  `r.matchers`.

## 5. Edge cases and constraints

- `pairs` itself is not modified.
- Not safe for concurrent use on the same route (it mutates the route).

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

## Helper contract: `addRegexpMatcher`

```go
// addRegexpMatcher adds a host, path, path-prefix or query matcher and builder
// to the route. If r.err is already non-nil it returns r.err unchanged and does
// nothing. Otherwise it parses the template (for regexpTypeQuery the template is
// "key=value", where value may contain {name} / {name:pattern} variables) and,
// on success, appends the new *routeRegexp to r.regexp.queries and to
// r.matchers and returns nil. It returns (without modifying the route) an error
// for malformed templates, e.g.
//   mux: unbalanced braces in "foo={bar"
//   mux: missing name or pattern in "{}"
//   a regexp compile error for an invalid variable pattern
//   mux: duplicated route variable "v1"   (a variable name already used by the
//                                           route's host, or by any of its
//                                           query templates)
func (r *Route) addRegexpMatcher(tpl string, typ regexpType) error
```

=== STUB ===
```go
func (r *Route) Queries(pairs ...string) *Route {
    // TODO: implement according to the specification
}
```
