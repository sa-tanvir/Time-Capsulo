# Functional specification: `cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)`

## 1. Component overview

A module-level helper of `requests.cookies`. It inserts the name/value pairs of
a plain mapping into a cookie jar (creating a new `RequestsCookieJar` if none
is given) and returns the jar. It is how `requests` turns `cookies={...}`
arguments into cookie jars, and is also used to merge dict cookies into an
existing jar without clobbering cookies already there.

## 2. Functional requirements

1. If `cookiejar` is `None`, a new empty `RequestsCookieJar()` is used.
   Otherwise the given jar (any `cookielib.CookieJar`, including a plain
   `http.cookiejar.CookieJar`) is modified **in place**.
2. If `cookie_dict` is `None`, nothing is inserted.
3. Otherwise, for every key `name` of `cookie_dict`, in the mapping's
   iteration order, a cookie is created with `create_cookie(name,
   cookie_dict[name])` (domain `''`, path `'/'`, all other attributes at
   their defaults) and stored with the jar's `set_cookie` method — unless
   `overwrite` is false and the jar **already contained, before this call
   started,** a cookie with that name (on any domain/path). With
   `overwrite=False`, names present only because they were added earlier in
   the same call do not block later insertions (a mapping cannot contain
   duplicate keys anyway).
4. When a cookie with the same name, domain `''` and path `'/'` already
   exists and is not protected by `overwrite=False`, storing the new cookie
   replaces it (normal cookie-jar semantics).
5. Return the jar (the same object that was passed in, or the newly created
   one).

## 3. Input specification

- `cookie_dict`: a mapping of cookie name (`str`) to value (`str`), or
  `None`.
- `cookiejar`: `None` or a `cookielib.CookieJar` instance.
- `overwrite`: `bool`; when false, existing names in the jar win.

## 4. Output specification

The cookie jar containing the original cookies plus the inserted ones.

Examples:
- `cookiejar_from_dict({'foo': 'bar'})` → new `RequestsCookieJar` with one
  cookie `foo=bar` (domain `''`, path `'/'`); `jar['foo'] == 'bar'`.
- `cookiejar_from_dict({'foo': 'bar'}, cj)` with `cj = http.cookiejar.CookieJar()`
  → returns `cj` itself, now holding cookie `foo`.
- jar containing `a=1` (domain `example.com`): `cookiejar_from_dict({'a': '2',
  'b': '3'}, jar, overwrite=False)` → `a` is not added (jar keeps only
  `a=1` for that name), `b=3` is added.
- same jar with `overwrite=True` → a second cookie `a=2` with domain `''` is
  added alongside the `example.com` one.
- `cookiejar_from_dict(None, jar)` → `jar` unchanged.

## 5. Edge cases and constraints

- Must not modify `cookie_dict`.
- Works with plain `cookielib.CookieJar` objects, which lack the dict-like
  helpers of `RequestsCookieJar`; only iteration over cookies and
  `set_cookie` may be assumed.
- An empty mapping returns the jar unchanged.
- Cookie values are stored as given; a `RequestsCookieJar` strips escaped
  quotes from `"..."`-wrapped values in its own `set_cookie`.
