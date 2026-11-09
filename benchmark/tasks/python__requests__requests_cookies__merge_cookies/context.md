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
