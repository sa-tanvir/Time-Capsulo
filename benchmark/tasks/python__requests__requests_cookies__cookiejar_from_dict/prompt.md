You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `requests/cookies.py`

## Imports / includes available in this file

```
import copy
import time
import calendar
from ._internal_utils import to_native_string
from .compat import cookielib, urlparse, urlunparse, Morsel, MutableMapping
```

## Other functions defined in the same file (signatures only; you may call them)

```
_copy_cookie_jar( jar )
_find( self , name , domain = None , path = None )
_find_no_duplicates( self , name , domain = None , path = None )
add_header( self , key , val )
add_unredirected_header( self , name , value )
copy( self )
create_cookie( name , value , ** kwargs )
extract_cookies_to_jar( jar , request , response )
get( self , name , default = None , domain = None , path = None )
get_cookie_header( jar , request )
get_dict( self , domain = None , path = None )
get_full_url( self )
get_header( self , name , default = None )
get_host( self )
get_new_headers( self )
get_origin_req_host( self )
get_policy( self )
get_type( self )
getheaders( self , name )
has_header( self , name )
host( self )
info( self )
is_unverifiable( self )
items( self )
iteritems( self )
iterkeys( self )
itervalues( self )
keys( self )
list_domains( self )
list_paths( self )
merge_cookies( cookiejar , cookies )
morsel_to_cookie( morsel )
multiple_domains( self )
origin_req_host( self )
remove_cookie_by_name( cookiejar , name , domain = None , path = None )
set( self , name , value , ** kwargs )
set_cookie( self , cookie , * args , ** kwargs )
unverifiable( self )
update( self , other )
values( self )
```

## Notes

- `create_cookie(name, value, **kwargs)` returns a `cookielib.Cookie` for domain `''`, path `'/'` (a "supercookie")
  with the other attributes defaulted; keyword arguments override attributes.
- `RequestsCookieJar` (defined in this module) is a `cookielib.CookieJar` with a dict-like interface; `RequestsCookieJar()`
  creates an empty jar.
- Iterating any `cookielib.CookieJar` yields its `Cookie` objects (attributes `name`, `value`, `domain`, `path`);
  `jar.set_cookie(cookie)` stores a cookie, replacing one with the same domain, path and name.

=== STUB ===
```python
def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
    raise NotImplementedError  # TODO: implement according to the specification
```
