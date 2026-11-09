You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `requests/cookies.py`
- **Enclosing scope:** `class RequestsCookieJar(cookielib.CookieJar, MutableMapping)`

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

## Instance state

- `self` is a `RequestsCookieJar`, a `cookielib.CookieJar` (`http.cookiejar`). Iterating it (`for cookie in self` /
  `iter(self)`) yields `cookielib.Cookie` objects, sorted by domain, then path, then name.
- Each cookie has the attributes `name` (`str`), `value` (`str` or `None`), `domain` (`str`, `''` for none) and
  `path` (`str`, default `'/'`).
- `class CookieConflictError(RuntimeError)` is defined in this module ("There are two cookies that meet the criteria
  specified in the cookie jar. Use .get and .set and include domain and path args in order to be more specific.").
- Callers: `get(name, default, domain, path)` returns `default` on `KeyError`; `__getitem__(name)` calls this method
  with only `name`.

=== STUB ===
```python
def _find_no_duplicates(self, name, domain=None, path=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
