# Functional specification: `func (r *Router) Match(req *http.Request, match *RouteMatch) bool`

## 1. Component overview

`(*Router).Match` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). It attempts to match a request against the router's
registered routes (and, through them, its subrouters). If a route matches, the
`Route`, `Handler` and `Vars` fields of `match` are filled and it returns
`true`. If no route matches, it returns `false` and records the reason in
`match.MatchErr`; if a handler is registered for that failure type
(`NotFoundHandler`, `MethodNotAllowedHandler`), that handler is put in
`match.Handler` and `true` is returned instead. `ServeHTTP` calls it and then
runs `match.Handler`; subrouters are matched by calling their `Match` from the
parent route.

## 2. Functional requirements

1. **Routes in registration order.** Call `route.Match(req, match)` for each
   route in `r.routes`, in order, passing the same `match`. Stop at the first
   route that returns `true`.
2. **Middleware on success.** When a route matched and `match.MatchErr` is
   `nil`, wrap `match.Handler` with the router's middlewares so that the
   middleware added **first** with `Use` is the **outermost** one: apply them
   from the last to the first, each time replacing `match.Handler` with
   `mw.Middleware(match.Handler)`. With middlewares `mw0, mw1` and route
   handler `h`, the final handler behaves as `mw0(mw1(h))`. When a route
   matched but `match.MatchErr` is non-nil (e.g. a subrouter answered with its
   own not-found handler and left `ErrNotFound`), the handler is **not**
   wrapped. In both cases return `true`.
3. **Method not allowed.** If no route matched and `match.MatchErr` is
   `ErrMethodMismatch` (some route matched everything except the method): if
   `r.MethodNotAllowedHandler` is non-nil, set `match.Handler` to it and
   return `true` (`MatchErr` stays `ErrMethodMismatch`); otherwise return
   `false` (with `MatchErr` still `ErrMethodMismatch`, `Handler` unchanged).
4. **Not found.** Otherwise, set `match.MatchErr = ErrNotFound`. If
   `r.NotFoundHandler` is non-nil, also set `match.Handler` to it and return
   `true`; else return `false`.
5. Middlewares are never applied to the not-found or method-not-allowed
   handlers.

Examples:

| router | request | result |
|---|---|---|
| `Path("/products/")` named `stock` | `GET http://www.example.com/products/` | `true`, `Route` = that route, `MatchErr = nil` |
| same | `GET .../products` | `false`, `MatchErr = ErrNotFound`, `Handler = nil` |
| `Host("www.example.com").Subrouter()` with child `Path("/products/")` | `GET http://www.example.com/products/` | `true`, `Route` = the child route |
| `HandleFunc("/", h).Methods("GET","POST")` | `PUT /` | `false`, `MatchErr = ErrMethodMismatch` |
| plus a second route `HandleFunc("/", h2).Methods("PUT")` | `PUT /` | `true`, `MatchErr = nil`, `Handler` = `h2` (wrapped by middlewares) |
| `Methods("GET")` route, `MethodNotAllowedHandler = h405`, `NotFoundHandler = h404`, one middleware | `POST /` | `true`, `Handler = h405` (unwrapped), `MatchErr = ErrMethodMismatch` |
| same | `GET /x` (no route) | `true`, `Handler = h404`, `MatchErr = ErrNotFound` |
| `HandleFunc("/", h)`, `PathPrefix("/sub/").Subrouter()` with child `HandleFunc("/", h)` | `GET /sub/whatever` | `false`, `MatchErr = ErrNotFound` |
| same, subrouter has `NotFoundHandler = s404` | `GET /sub/whatever` | `true`, `Handler = s404`, `MatchErr = ErrNotFound`, no middleware applied |
| no routes, `NotFoundHandler = h404` | anything | `true`, `Handler = h404`, `MatchErr = ErrNotFound` |
| strict-slash route `Path("/111/")`, middlewares `mw0, mw1` | `GET /111` | `true`, `Handler` = `mw0(mw1(redirect to /111/))` |

## 3. Input specification

- `r`: a router with zero or more routes (possibly hundreds, possibly with
  subrouters), zero or more middlewares, and optional `NotFoundHandler` /
  `MethodNotAllowedHandler`.
- `req`: an `*http.Request` with non-nil `URL` and `Header`.
- `match`: non-nil; usually zero-valued (when called for a subrouter it holds
  the state of the parent's matching so far).

## 4. Output specification

- `bool` as described; `match` updated (`Route`, `Handler`, `Vars` by the
  matching route; `Handler` possibly wrapped by middlewares or set to a
  failure handler; `MatchErr` as described).

## 5. Edge cases and constraints

- The router, its routes and the request are not modified.
- Middleware functions are invoked (to build the chain) once per successful
  match; the resulting handler is not executed by `Match`.
- Safe for concurrent use with distinct `match` values, provided the
  middleware functions are.
