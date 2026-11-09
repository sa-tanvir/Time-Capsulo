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
