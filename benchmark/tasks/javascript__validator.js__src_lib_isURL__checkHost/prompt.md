You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isURL.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import isFQDN from './isFQDN';
import isIP from './isIP';
import merge from './util/merge';
```

## Other functions defined in the same file (signatures only; you may call them)

```
isRegExp ( obj )
isURL ( url , options )
```

## Variables declared at the same scope level (you may use them)

```
const default_url_options = {
  protocols: ['http', 'https', 'ftp'],
  require_tld: true,
  require_protocol: false,
  require_host: true,
  require_valid_protocol: true,
  allow_underscores: false,
  allow_trailing_dot: false,
  allow_protocol_relative_urls: false,
};
const wrapped_ipv6 = /^\[([^\]]+)\](?::([0-9]+))?$/;
```

## Behaviour of the sibling helper

- `isRegExp(obj)` (same file): returns `true` when `Object.prototype.toString.call(obj)` is
  `'[object RegExp]'`, i.e. `obj` is a regular expression object; `false` otherwise.

=== STUB ===
```javascript
function checkHost(host, matches) {
    // TODO: implement according to the specification
}
```
