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
