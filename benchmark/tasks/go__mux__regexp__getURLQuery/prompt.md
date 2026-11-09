You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *routeRegexp) getURLQuery(req *http.Request) string`

## 1. Component overview

`getURLQuery` belongs to the `mux` package (`github.com/gorilla/mux`, an HTTP
request router). A route created with `Queries("foo", "{v1}")` owns one
`routeRegexp` of type `regexpTypeQuery` per key/value pair, with template
`"foo={v1}"` (see the *Instance state* section of the context). To match such a
template, the router does not look at the whole query string: it extracts the
single parameter named by the template from the request URL and renders it as
`key=value`. `getURLQuery` performs this extraction; its result is then matched
against the template's regexp (e.g. `^foo=(?P<v0>.*)$`) and used to extract
route variables.

## 2. Functional requirements

1. **Non-query templates.** If `r.regexpType` is not `regexpTypeQuery`, return
   `""` without inspecting the request.
2. **Template key.** The key is the part of `r.template` before the first `=`
   (`"foo={v1}"` → `"foo"`, `"foo="` → `"foo"`). It is used exactly as written
   (it is not unescaped).
3. **Request parameters.** Parse the request's raw query with
   `req.URL.Query()` (standard `net/url` parsing: pairs separated by `&` (and
   `;` in this Go version), `+` and percent-escapes decoded in keys and values,
   a pair without `=` has the empty value, pairs with invalid escapes are
   dropped).
4. **Result.** If the parsed query contains the template key with at least one
   value, return `key + "=" + firstValue`, where `firstValue` is the
   **decoded** value of the first occurrence of that key in the query string.
   Otherwise return `""`.
5. Only exact key equality counts (`"fffoo"` is not `"foo"`; keys are
   case-sensitive).

Examples (template → raw query → result):

| template | raw query | result |
|---|---|---|
| `foo=bar` | `foo=bar&baz=ding` | `"foo=bar"` |
| `baz=ding` | `foo=bar&baz=dong` | `"baz=dong"` |
| `foo={v1}` | `bar=2&foo=1` | `"foo=1"` |
| `foo=` | `` (empty) | `""` |
| `foo=` | `foo=` | `"foo="` |
| `foo=` | `foo` | `"foo="` |
| `foo=bar` | `fffoo=bar&baz=dingggg` | `""` |
| `foo={v1}` | `foo=%25bar%26%20%2F%3D%3F` | `"foo=%bar& /=?"` |
| `foo={v1}` | `foo=a&foo=b` | `"foo=a"` |
| `foo={v1}` | `foo=a+b` | `"foo=a b"` |
| `foo={v1}` | `foo=%zz&foo=2` | `"foo=2"` (invalid pair dropped) |
| `f o={v1}` | `f+o=1` | `"f o=1"` |
| `/foo` (path type) | `foo=bar` | `""` |

## 3. Input specification

- `r`: a `routeRegexp` built by `newRouteRegexp`; query templates always
  contain `=`.
- `req`: an `*http.Request` with non-nil `URL`; only `req.URL.RawQuery` is
  relevant. Query strings may hold from zero to several hundred parameters,
  with repeated keys and percent-encoded or `+`-encoded characters.

## 4. Output specification

- A `string`: `""` or `key=value` with the decoded value, as above.

## 5. Edge cases and constraints

- `r` and `req` are not modified (the URL's raw query is only read).
- The value is returned decoded and is not re-escaped.
- Safe for concurrent use.

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
(r*routeRegexp)matchQueryString req * http . Request
(r*routeRegexp)url values map [ string ] string
(v routeRegexpGroup)setMatch req * http . Request , m * RouteMatch , r * Route
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

=== STUB ===
```go
func (r *routeRegexp) getURLQuery(req *http.Request) string {
    // TODO: implement according to the specification
}
```
