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
