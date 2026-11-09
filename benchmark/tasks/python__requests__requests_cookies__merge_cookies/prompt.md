You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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
cookiejar_from_dict( cookie_dict , cookiejar = None , overwrite = True )
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

- `cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)`: inserts each name/value of the mapping as a
  default cookie (domain `''`, path `'/'`) into `cookiejar` (a new `RequestsCookieJar` if `None`) and returns that jar;
  with `overwrite=False`, names already present in the jar are skipped.
- `RequestsCookieJar.update(other)`: for a `cookielib.CookieJar` `other`, stores `copy.copy(cookie)` for each cookie
  via `set_cookie`; otherwise behaves like `MutableMapping.update`.
- A plain `cookielib.CookieJar` has `set_cookie(cookie)` and is iterable over its cookies, but has no `update` method.

=== STUB ===
```python
def merge_cookies(cookiejar, cookies):
    raise NotImplementedError  # TODO: implement according to the specification
```
