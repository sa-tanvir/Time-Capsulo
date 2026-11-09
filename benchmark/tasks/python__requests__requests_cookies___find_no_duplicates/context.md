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
