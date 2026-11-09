You are an expert Go developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Go code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```go code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `func (r *routeRegexp) url(values map[string]string) (string, error)`

## 1. Component overview

`url` belongs to the `mux` package (`github.com/gorilla/mux`, an HTTP request
router). A `routeRegexp` is the compiled form of one route template (a host,
path, path-prefix or query template; see the *Instance state* section of the
context). `url` performs **reverse routing** for that template: it fills the
template's variables with the given values and returns the resulting URL part.
`Route.URL`, `Route.URLHost` and `Route.URLPath` call it for the route's host,
path and each query template, e.g. route
`Host("{subdomain}.domain.com").Path("/articles/{category}/{id:[0-9]+}")`
with values `subdomain=foo, category=technology, id=42` builds
`http://foo.domain.com/articles/technology/42`.

## 2. Functional requirements

1. **All variables are required.** For each variable name in `r.varsN`, in
   order, look it up in `values`. If a name is missing from the map (a present
   key with value `""` counts as present), return `""` and an error whose
   message is exactly `mux: missing route variable "<name>"` (the name quoted
   as with Go's `%q`). The first missing name in `varsN` order is reported.
   Keys of `values` that are not variables of this template are ignored.
2. **Query values are escaped.** For a query template (`regexpTypeQuery`),
   each value is escaped with `url.QueryEscape` before substitution (space →
   `+`, `%` → `%25`, `&` → `%26`, `/` → `%2F`, `=` → `%3D`, `?` → `%3F`). For
   host, path and prefix templates values are inserted verbatim.
3. **Substitution.** The result is the template with every `{...}` token
   replaced by its (possibly escaped) value and all literal text unchanged; it
   has the same shape as `r.reverse` with the values filled in. Templates
   without variables yield their literal text (`"/111/"` → `"/111/"`,
   `"foo="` → `"foo="`, `""` → `""`).
4. **Validation.** If the substituted string matches the whole-template
   regexp `r.regexp`, return it with a `nil` error. Otherwise check each
   variable's **raw, unescaped** value against its own validator `r.varsR[k]`,
   in `varsN` order; for the first one that does not match, return `""` and an
   error with message exactly
   `mux: variable "<value>" doesn't match, expected "<validator>"`, where both
   parts are quoted as with `%q` and `<validator>` is `r.varsR[k].String()`
   (e.g. `^[0-9]+$`). If every individual value matches its validator (this
   can happen when escaping changed the value), return the substituted string
   with a `nil` error even though the whole regexp did not match.

Examples:

| template (type) | values | result |
|---|---|---|
| `/articles/{category}/{id:[0-9]+}` (path) | category=technology, id=42 | `"/articles/technology/42"`, nil |
| same | category=technology, id=x | `""`, `mux: variable "x" doesn't match, expected "^[0-9]+$"` |
| same | category=technology | `""`, `mux: missing route variable "id"` |
| `{v1:[a-z]+}.google.com` (host) | v1=Bad | `""`, `mux: variable "Bad" doesn't match, expected "^[a-z]+$"` |
| `{a}.{b}` (host) | a=x.y, b=z | `""`, `mux: variable "x.y" doesn't match, expected "^[^.]+$"` |
| `/a/{v1}` (path) | v1=x/y | `""`, `mux: variable "x/y" doesn't match, expected "^[^/]+$"` |
| `/{a:[0-9]+}/{b:[0-9]+}` | a=x, b=y | error names `"x"` (first in order) |
| `/{v1}/` (path, strict slash) | v1=x | `"/x/"`, nil |
| `/static/` (prefix) | none | `"/static/"`, nil |
| `foo={v1}` (query) | v1=`%bar& /=?` | `"foo=%25bar%26+%2F%3D%3F"`, nil |
| `foo={v1:[0-9]+}` (query) | v1=`1 0` | `""`, `mux: variable "1 0" doesn't match, expected "^[0-9]+$"` |
| `foo={v1:[a-z ]+}` (query) | v1=`a b` | `"foo=a+b"`, nil (raw value is valid) |

## 3. Input specification

- `r`: a `routeRegexp` produced by `newRouteRegexp` (fields as described in
  the context). Templates contain from zero to a few hundred variables and
  never contain the character `%`.
- `values`: variable name → value; may be `nil` (only valid when the template
  has no variables) and may contain extra keys. Values are arbitrary strings.

## 4. Output specification

- `(string, nil)` on success; `("", error)` on failure with the exact messages
  above (tests compare built URLs; error text is created with `fmt.Errorf`).

## 5. Edge cases and constraints

- `r` and `values` are not modified.
- A value of `""` is present, not missing; it then fails validation unless the
  variable's pattern accepts the empty string.
- No escaping is applied to path/host values (`"1%2F2"` is inserted as is).
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
(r*routeRegexp)getURLQuery req * http . Request
(r*routeRegexp)matchQueryString req * http . Request
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
func (r *routeRegexp) url(values map[string]string) (string, error) {
    // TODO: implement according to the specification
}
```
