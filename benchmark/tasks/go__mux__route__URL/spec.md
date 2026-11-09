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
