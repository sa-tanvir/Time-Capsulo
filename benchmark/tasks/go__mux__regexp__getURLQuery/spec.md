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
