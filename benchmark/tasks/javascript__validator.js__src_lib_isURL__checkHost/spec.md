# Functional specification: `checkHost(host, matches)` in `src/lib/isURL.js`

## 1. Component overview

Module-private helper of the validator.js URL validator. `isURL(url, options)` uses it to apply
the `host_whitelist` and `host_blacklist` options: after extracting the host name of a URL it
asks whether that host is matched by any entry of the list. Entries are either exact host
strings or regular expressions.

## 2. Functional requirements

1. Examine the entries of `matches` in index order (from 0 to `matches.length - 1`).
2. An entry matches when either
   - it is strictly equal (`===`) to `host` (so string entries match only the identical string;
     comparison is case-sensitive), or
   - it is a regular expression object (as recognised by `isRegExp`, see context) and testing
     it against `host` succeeds (i.e. `RegExp.prototype.test(host)` returns `true`; the pattern
     may match anywhere unless it is anchored).
3. Return `true` as soon as an entry matches (later entries are not examined); return `false`
   if no entry matches, including when `matches` is empty.

## 3. Input specification

- `host`: a string (a host name such as `'images.foo.com'`, or an IPv6 address); may be empty.
- `matches`: an array whose elements are strings and/or `RegExp` objects (without the `g` or
  `y` flags). It may be empty and may be long (thousands of entries).

## 4. Output specification

A boolean.

Examples with `matches = ['bar.com', 'foo.com', /\.foo\.com$/]`:

- `checkHost('bar.com', matches)` → `true`; `checkHost('foo.com', matches)` → `true`
- `checkHost('images.foo.com', matches)` → `true`; `'cdn.foo.com'`, `'a.b.c.foo.com'` → `true`
- `checkHost('foobar.com', matches)` → `false`; `'foo.bar.com'`, `'qux.com'` → `false`

With `matches = ['foo.com', 'bar.com']`: `'foo.com'` → `true`, `'images.foo.com'` → `false`,
`'FOO.com'` → `false`. With `matches = []` every host gives `false`.

Through `isURL`: with `host_whitelist: ['foo.com', 'bar.com']`, `'http://foo.com/'` is valid and
`'http://foobar.com'` is not; with the same list as `host_blacklist` the results are inverted.

## 5. Edge cases and constraints

- Must not modify `host` or `matches`.
- Substring containment of a string entry is **not** a match (`'foo.com'` does not match
  `'images.foo.com'`); only regular expressions can match partially.
- Elements that are neither equal to `host` nor regular expressions never match.
