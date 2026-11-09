# Functional specification: `RequestsCookieJar._find_no_duplicates(self, name, domain=None, path=None)`

## 1. Component overview

A lookup method of `RequestsCookieJar`, the dict-like cookie jar of the
`requests` library (a subclass of `http.cookiejar.CookieJar`). It backs both
`jar[name]` and `jar.get(name, default, domain, path)`: it finds the value of
the single cookie matching a name and, optionally, a domain and a path, and
refuses to guess when the criteria are ambiguous.

## 2. Functional requirements

1. Consider every cookie in the jar, in the jar's normal iteration order
   (`iter(self)`).
2. A cookie **matches** when all of the following hold:
   - `cookie.name == name`;
   - `domain is None`, or `cookie.domain == domain` (exact string equality,
     no suffix/dot matching);
   - `path is None`, or `cookie.path == path` (exact string equality).
3. **Conflicts.** Walk the matching cookies in iteration order and remember
   the value of the latest one. When a matching cookie is found while the
   remembered value is not `None` (i.e. an earlier match had a value other
   than `None`; an empty string `''` counts), raise `CookieConflictError`
   with the message `'There are multiple cookies with name, %r' % (name)`
   (e.g. `"There are multiple cookies with name, 'some_cookie'"`). This
   happens even if both cookies have the same value. A matching cookie whose
   value is `None` does not block later matches: if only `None`-valued
   matches precede it, the next match is accepted without a conflict.
   Example: two cookies `some_cookie` set for domains `test1.com` and
   `test2.com` → conflict when `domain` is `None`, but `domain='test1.com'`
   returns that cookie's value. Likewise a cookie with path `some_path` and
   one with path `/` conflict when `path` is `None`.
4. After the walk, if the remembered value is truthy, return it
   (`cookie.value`, normally a `str`).
5. Otherwise raise `KeyError` whose single argument is the string
   `'name=%r, domain=%r, path=%r' % (name, domain, path)`, e.g.
   `"name='x', domain=None, path=None"`. This includes the case where no
   cookie matches **and** the case where the last remembered value is falsy
   (`''` or `None`): such a cookie is treated as not found.

Values of the matching cookies, in iteration order → result:
`['a']` → `'a'`; `[None, 'a']` → `'a'`; `['a', None]`, `['', 'a']`,
`['a', 'a']`, `[None, 'a', 'b']` → `CookieConflictError`; `[None]`,
`[None, None]`, `[None, '']`, `['']` → `KeyError`.

## 3. Input specification

- `self`: a `RequestsCookieJar` (see "Instance state" in the context).
- `name`: `str`, the cookie name.
- `domain`: `str` or `None` (no domain filter).
- `path`: `str` or `None` (no path filter).

## 4. Output specification

The matching cookie's value. Never returns `None` or `''`; those situations
raise `KeyError` as described.

## 5. Edge cases and constraints

- Read-only: must not add, remove or modify cookies.
- Empty jar → `KeyError`.
- `CookieConflictError` takes precedence over `KeyError`: it is raised as
  soon as a match follows an earlier match with a non-`None` value (rule 3),
  whatever the values are.
- Matching is case-sensitive for name, domain and path.
- `CookieConflictError` is a `RuntimeError` subclass defined in this module.
