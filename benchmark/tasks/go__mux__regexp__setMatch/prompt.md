You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (v routeRegexpGroup) setMatch(req *http.Request, m *RouteMatch, r *Route)`

## 1. Component overview

`setMatch` belongs to the `mux` package (`github.com/gorilla/mux`, an HTTP
request router). Once `(*Route).Match` has decided that route `r` matches a
request, it calls `r.regexp.setMatch(req, match, r)` to fill
`match.Vars` with the route variables taken from the request's host, path and
query string, and, for strict-slash routes, to install a redirect handler when
the request's trailing slash differs from the template's. The receiver `v` is
the route's group of templates (`host`, `path`, `queries`; each a
`*routeRegexp`, see the context). For example, the route
`Host("{v1}.domain.com").Path("/{v2}/{v3}").Queries("foo", "{v4}")` and the
request `http://aaa.domain.com/bbb/ccc?foo=ddd` yield
`Vars = {v1: aaa, v2: bbb, v3: ccc, v4: ddd}`.

## 2. Functional requirements

`m.Vars` is a non-nil map supplied by the caller; variables are added to it
(existing entries with other names are kept, same names are overwritten).

1. **Host variables.** If `v.host` is non-nil, take the request host
   (`getHost(req)`: `req.URL.Host` for absolute URLs, else `req.Host`) and
   search it with `v.host.regexp`. If it matches, store each host variable
   (`v.host.varsN[i]`) with the text captured by its group. If it does not
   match, store nothing for the host.
2. **Path.** The path used is `req.URL.Path`, or `req.URL.EscapedPath()` if
   the **route** `r` has `useEncodedPath` set (the route's flag, not the
   template's option, decides). If `v.path` is non-nil and its regexp matches
   this path, store the path variables the same way. Otherwise nothing is
   stored for the path and no redirect is considered.
3. **Strict-slash redirect.** Only when the path matched and
   `v.path.options.strictSlash` is `true`: let *A* = "the path used in rule 2
   ends with `/`" and *B* = "`v.path.template` ends with `/`". If *A* ≠ *B*,
   set `m.Handler` to `http.RedirectHandler(target, http.StatusMovedPermanently)`
   where `target` is obtained by parsing `req.URL.String()` with `url.Parse`,
   then removing the final `/` from its `Path` (when *A*) or appending `/` to
   it (when *B*), and rendering it again with `String()`. Scheme, host, query
   and fragment are preserved: `http://localhost/foo/123/?a=b#frag` against
   template `/{arg1}/{arg2:[0-9]+}` redirects to
   `http://localhost/foo/123?a=b#frag`. If *A* = *B*, `m.Handler` is left
   unchanged. Prefix templates never have `strictSlash` set.
4. **Query variables.** For each query template `q` in `v.queries`, in order,
   take `q.getURLQuery(req)` (e.g. `"foo=ddd"`) and search it with `q.regexp`;
   if it matches, store `q`'s variables from it (values are therefore
   decoded: `?foo=%25bar%26%20%2F%3D%3F` with `foo={v1}` gives
   `v1 = "%bar& /=?"`). Non-matching query templates store nothing.
5. Each part is handled independently; a non-matching part never prevents the
   others from being processed. Nothing else in `m` is changed.

Examples (route → request → `Vars`, handler):

| route | request | Vars | handler |
|---|---|---|---|
| `Path("/111/")`, strict | `http://localhost/111` | `{}` | redirect to `http://localhost/111/` |
| `Path("/111/")`, strict | `http://localhost/111/` | `{}` | unchanged (nil) |
| `Path("/{arg1}/{arg2:[0-9]+}/")`, strict | `http://localhost/foo/123` | `{arg1: foo, arg2: 123}` | redirect to `http://localhost/foo/123/` |
| `PathPrefix("/static/")`, strict router | `http://localhost/static/logo.png` | `{}` | unchanged |
| `Path("/v1/{v1}/v2")`, route uses encoded path | `http://localhost/v1/1%2F2/v2` | `{v1: 1%2F2}` | unchanged |
| `Path("/v1/{v1}/v2")`, decoded path | same request | `{}` (path `/v1/1/2/v2` does not match) | unchanged |
| `Host("{foo:[a-z][a-z][a-z]}.{bar:[a-z][a-z][a-z]}.{baz:[a-z][a-z][a-z]}")` | `http://abc.def.ghi/` | `{foo: abc, bar: def, baz: ghi}` | unchanged |
| `Host("{sub}.example.com")` | relative URL `/rel`, `req.Host = "news.example.com"` | `{sub: news}` | unchanged |
| `Queries("foo", "{v1}", "baz", "{v2}")` | `?foo=bar&baz=ding` | `{v1: bar, v2: ding}` | unchanged |
| `Queries("foo", "{v1:[0-9]+}")` | `?foo=a` | `{}` | unchanged |

## 3. Input specification

- `v`: the route's template group (`host`, `path` may be nil; `queries` may be
  empty). Templates may carry up to a few hundred variables.
- `req`: a request with non-nil `URL` (absolute or relative). Callers guarantee
  that `req.URL.String()` parses again with `url.Parse` without error; a parse
  failure during the redirect of rule 3 is outside the contract (the original
  does not check the error and panics with a nil-pointer dereference there).
- `m`: non-nil; `m.Vars` is a non-nil map.
- `r`: the route that owns `v`; only `r.useEncodedPath` is consulted.

## 4. Output specification

- No return value. Effects: entries added to `m.Vars`; possibly `m.Handler`
  replaced by a 301 redirect handler (rule 3).

## 5. Edge cases and constraints

- `req`, `v` and `r` are not modified.
- Variable values are the raw captured substrings (no decoding of the path or
  host; query values come already decoded from the query parsing).
- When several templates define the same name, later parts (path after host,
  queries after path) overwrite earlier ones.
- Safe for concurrent use as long as each call gets its own `m`.

=== CONTEXT ===
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

=== STUB ===
```go
func (v routeRegexpGroup) setMatch(req *http.Request, m *RouteMatch, r *Route) {
    // TODO: implement according to the specification
}
```
