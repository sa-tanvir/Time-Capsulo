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
