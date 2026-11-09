# Functional specification: `func (r *Route) Match(req *http.Request, match *RouteMatch) bool`

## 1. Component overview

`(*Route).Match` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). A route is a list of matchers (host/path/query
templates, methods, headers, schemes, custom functions, subrouters) added with
the fluent builder API. `(*Router).Match` calls `route.Match(req, &match)` for
each registered route in turn until one returns `true`; the same
`RouteMatch` value is passed to every route, so its `MatchErr` carries
information between routes (e.g. "some route matched everything except the
HTTP method", which lets the router answer 405 instead of 404). On success the
match receives the route, its handler and the route variables.

## 2. Functional requirements

1. **Unusable routes.** If the route is build-only (`r.buildOnly`) or has a
   build error (`r.err != nil`), return `false` without touching `match`.
2. **Run every matcher in order.** Call `m.Match(req, match)` for each
   matcher `m` in `r.matchers`:
   - If a matcher of type `methodMatcher` fails, remember a method mismatch
     and **continue** with the next matchers.
   - If any other matcher fails: if `match.MatchErr` is currently
     `ErrNotFound` (left there, e.g., by a subrouter that found nothing), reset
     it to `nil`; forget any remembered method mismatch; return `false`
     immediately. (Any other `MatchErr` value, including `ErrMethodMismatch`
     set earlier, is left as is.)
3. **Only the method failed.** If all non-method matchers succeeded but a
   method matcher failed, set `match.MatchErr = ErrMethodMismatch` and return
   `false` (no other field is changed).
4. **Full match.** Otherwise the route matches:
   1. If `match.MatchErr` is `ErrMethodMismatch` (an earlier route matched
      everything but the method), set `match.MatchErr = nil` and set
      `match.Handler = r.handler`, overriding any handler already there.
      Any other `MatchErr` value (e.g. `ErrNotFound`) is left unchanged.
   2. If `match.Route` is `nil`, set it to `r` (a route already set — e.g. by
      a subrouter matcher — is kept).
   3. If `match.Handler` is `nil`, set it to `r.handler`.
   4. If `match.Vars` is `nil`, set it to a new empty map.
   5. Call `setMatch` on the route's template group (`r.regexp`), passing the request, the match and the route itself, to add the route variables (and
      a possible strict-slash redirect handler).
   6. Return `true`.

Examples:

| route | request / initial match | result |
|---|---|---|
| `Methods("GET","POST")` | `PUT`, empty match | `false`, `MatchErr = ErrMethodMismatch` |
| `Methods("GET").Path("/a")` | `PUT /b`, empty | `false`, `MatchErr = nil` |
| `Methods("GET").Path("/a")` | `PUT /b`, `MatchErr = ErrNotFound` | `false`, `MatchErr = nil` |
| `Methods("GET").Path("/a")` | `PUT /b`, `MatchErr = ErrMethodMismatch` | `false`, still `ErrMethodMismatch` |
| `Path("/a")` | `GET /a`, `MatchErr = ErrMethodMismatch`, `Handler = h0` | `true`, `MatchErr = nil`, `Handler = r.handler`, `Route = r`, `Vars = {}` |
| `Path("/a")` | `GET /a`, `MatchErr = ErrNotFound` | `true`, `MatchErr` stays `ErrNotFound`, `Route = r` |
| `Path("/{v}")` | `GET /a`, `Route = r0`, `Handler = h0`, `Vars = {pre: x}` | `true`, `Route = r0`, `Handler = h0`, `Vars = {pre: x, v: a}` |
| `Host("{v1}.google.com").Path("/{var2:[a-z]+}/{var3:[0-9]+}").Queries("foo","bar").Methods("GET").Schemes("https").Headers("x-requested-with","XMLHttpRequest")` | `GET https://www.google.com/product/42?foo=bar` with that header | `true`, `Vars = {v1: www, var2: product, var3: 42}` |
| same | `POST`, header present | `false`, `ErrMethodMismatch` |
| same | `POST`, header missing | `false`, `MatchErr = nil` |
| `Path("/111/")` with strict slash | `GET /111` | `true`, `Handler` = redirect to `/111/` |
| `PathPrefix("/sub").Subrouter()` + child `Path("/x/{c0}")` | `GET /sub/x/1` | `true`, `Route` = the child route, `Vars = {c0: 1}` |
| route with no matchers | anything | `true` |
| build-only or erroneous route | anything | `false`, match untouched |

## 3. Input specification

- `r`: a route built with the fluent API; up to a few hundred matchers /
  variables.
- `req`: an `*http.Request` with non-nil `URL` and `Header`.
- `match`: non-nil; may be zero-valued or carry state left by earlier routes
  (`MatchErr`, `Route`, `Handler`, `Vars`).

## 4. Output specification

- `bool`: whether the route matched; `match` updated as described.

## 5. Edge cases and constraints

- `r` and `req` are never modified.
- When `false` is returned, `Route`, `Handler` and `Vars` are not set by this
  route itself (a subrouter matcher may have written to them).
- Safe for concurrent use with distinct `match` values.
