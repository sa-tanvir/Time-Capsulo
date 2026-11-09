# Functional specification: `func matchMapWithRegex(toCheck map[string]*regexp.Regexp, toMatch map[string][]string, canonicalKey bool) bool`

## 1. Component overview

`matchMapWithRegex` belongs to the `mux` package (`github.com/gorilla/mux`, an
HTTP request router). It decides whether every required key of a multi-valued
map (such as an `http.Header`) carries a value accepted by a regular
expression. The route matcher created by
`Route.HeadersRegexp("Content-Type", "application/(text|json)", ...)` compiles
each pattern and calls `matchMapWithRegex(required, req.Header, true)`.

## 2. Functional requirements

Return `true` if and only if **every** entry `(k, re)` of `toCheck` is
satisfied by `toMatch`:

1. **Key lookup.** If `canonicalKey` is `true`, the key looked up in `toMatch`
   is `http.CanonicalHeaderKey(k)` (e.g. `"foo"` → `"Foo"`,
   `"x-requested-with"` → `"X-Requested-With"`); otherwise `k` is used exactly
   as given. The keys of `toMatch` are never transformed.
2. **Key must exist.** If the looked-up key is absent from `toMatch`, or maps
   to a `nil` slice, the entry is not satisfied.
3. **`nil` regexp = presence only.** If `re` is `nil`, the entry is satisfied
   as soon as the key exists with a non-`nil` slice (even an empty one).
4. **Otherwise at least one value must match.** If `re` is not `nil`, the entry
   is satisfied only if `re.MatchString(value)` is `true` for at least one
   value in the slice. Matching is the standard unanchored `regexp` search: a
   pattern matches if it matches any substring, unless the pattern itself uses
   `^`/`$` anchors. An empty (non-`nil`) slice therefore fails for a non-`nil`
   regexp, even one compiled from `""`.

An empty (or `nil`) `toCheck` yields `true`. Extra keys in `toMatch` and extra
values are ignored.

Examples (`canonicalKey = true`; patterns shown as their source text):

| `toCheck` | `toMatch` | result |
|---|---|---|
| `{"Accept": "html"}` | `{"Accept": ["text/plain", "text/html"]}` | `true` |
| `{"Accept": "html"}` | `{"Accept": ["application/xhtml+xml"]}` | `true` (substring) |
| `{"Origin": "^https://example.co$"}` | `{"Origin": ["https://example.co"]}` | `true` |
| `{"Origin": "^https://example.co$"}` | `{"Origin": ["https://example.co.uk"]}` | `false` |
| `{"foo": "ba[zr]"}` | `{"Foo": ["baz"]}` | `true` |
| `{"foo": "ba[zr]"}` | `{"Foo": ["bat"]}` | `false` |
| `{"foo": ""}` | `{"Foo": ["anything"]}` | `true` |
| `{"foo": ""}` | `{"Foo": []}` | `false` |
| `{"foo": nil}` | `{"Foo": []}` | `true` |
| `{"foo": nil}` | `{}` | `false` |
| `{"foo": "x"}`, `canonicalKey = false` | `{"Foo": ["x"]}` | `false` |
| `{}` | anything | `true` |

## 3. Input specification

- `toCheck`: required keys with compiled patterns (`*regexp.Regexp`, possibly
  `nil`); may be `nil` or empty; up to a few hundred entries; keys in any case.
- `toMatch`: available values per key (typically an `http.Header`); may be
  `nil`; slices may hold dozens of values.
- `canonicalKey`: whether `toCheck` keys must be canonicalised as MIME header
  keys before lookup.

## 4. Output specification

- `bool` as described in section 2. The result does not depend on map
  iteration order.

## 5. Edge cases and constraints

- Neither map nor any regexp is modified.
- Only keys are canonicalised; values are passed to the regexp unchanged.
- Never panics for valid inputs; safe for concurrent use as long as the maps
  are not written concurrently (compiled regexps are safe to share).
