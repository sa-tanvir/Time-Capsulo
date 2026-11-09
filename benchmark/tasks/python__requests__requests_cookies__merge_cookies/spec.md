# Functional specification: `merge_cookies(cookiejar, cookies)`

## 1. Component overview

A module-level helper of `requests.cookies` used when a `Session` combines its
own cookies with per-request cookies. It adds the cookies from `cookies` (a
dict or another cookie jar) into `cookiejar` and returns the resulting jar.

## 2. Functional requirements

1. If `cookiejar` is not an instance of `cookielib.CookieJar`, raise
   `ValueError('You can only merge into CookieJar')`. This check happens
   first, whatever `cookies` is.
2. If `cookies` is a `dict` (including subclasses such as `OrderedDict`):
   insert its entries into `cookiejar` **without overwriting**: a name that
   already exists in `cookiejar` (on any domain/path) is left alone, other
   names are added as default cookies (domain `''`, path `'/'`). This is
   exactly what `cookiejar_from_dict` does when given the target jar and
   overwriting disabled; its return value is the result.
3. Else, if `cookies` is a `cookielib.CookieJar`: add every cookie of
   `cookies` into `cookiejar`, replacing a cookie in `cookiejar` with the same
   domain, path and name (later cookies win).
   - If `cookiejar` has an `update` method (e.g. `RequestsCookieJar.update`,
     which stores a shallow copy of each cookie of the other jar), use it.
   - If calling `update` raises `AttributeError` (a plain
     `cookielib.CookieJar` has no `update`), fall back to storing each
     cookie of `cookies` (the cookie objects themselves) with
     `cookiejar.set_cookie(cookie)`.
4. Any other value of `cookies` (e.g. `None`) is ignored.
5. Return `cookiejar`. It is modified in place; the returned object is the
   same jar object that was passed in.

## 3. Input specification

- `cookiejar`: expected to be a `cookielib.CookieJar` (often a
  `RequestsCookieJar`).
- `cookies`: a `dict` of name → value, a `cookielib.CookieJar`, or anything
  else (ignored).

## 4. Output specification

The (mutated) `cookiejar`.

Examples:
- `merge_cookies(RequestsCookieJar(), {'foo': 'bar'})` → jar with `foo=bar`.
- session jar containing `foo=bar`; `merge_cookies(jar, {'foo': 'baz'})` →
  `foo` stays `bar` (dict cookies never overwrite).
- session jar containing `foo=bar` (domain `''`, path `'/'`); `other` jar
  containing `foo=baz` for the same domain/path; `merge_cookies(jar, other)`
  → `foo` becomes `baz` (jar cookies do overwrite).
- `merge_cookies({'a': 1}, {})` → `ValueError`.
- `merge_cookies(jar, None)` → `jar` unchanged.

## 5. Edge cases and constraints

- `cookies` is never modified.
- Cookies copied from another `RequestsCookieJar` via `update` are copies;
  in the plain-jar fallback the very same cookie objects are stored.
- The fallback must be triggered by an `AttributeError` raised by the
  attempt to update, not by a type test on `cookiejar`.
