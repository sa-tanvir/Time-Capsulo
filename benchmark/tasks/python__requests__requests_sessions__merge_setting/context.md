# Context for the function to implement

- **Language:** python
- **File:** `requests/sessions.py`

## Imports / includes available in this file

```
import os
import sys
import time
from datetime import timedelta
from .auth import _basic_auth_str
from .compat import cookielib, is_py3, OrderedDict, urljoin, urlparse, Mapping
from .cookies import (
    cookiejar_from_dict, extract_cookies_to_jar, RequestsCookieJar, merge_cookies)
from .models import Request, PreparedRequest, DEFAULT_REDIRECT_LIMIT
from .hooks import default_hooks, dispatch_hook
from ._internal_utils import to_native_string
from .utils import to_key_val_list, default_headers, DEFAULT_PORTS
from .exceptions import (
    TooManyRedirects, InvalidSchema, ChunkedEncodingError, ContentDecodingError)
from .structures import CaseInsensitiveDict
from .adapters import HTTPAdapter
from .utils import (
    requote_uri, get_environ_proxies, get_netrc_auth, should_bypass_proxies,
    get_auth_from_url, rewind_body
)
from .status_codes import codes
from .models import REDIRECT_STATI
```

## Other functions defined in the same file (signatures only; you may call them)

```
close( self )
delete( self , url , ** kwargs )
get( self , url , ** kwargs )
get_adapter( self , url )
get_redirect_target( self , resp )
head( self , url , ** kwargs )
merge_environment_settings( self , url , proxies , stream , verify , cert )
merge_hooks( request_hooks , session_hooks , dict_class = OrderedDict )
mount( self , prefix , adapter )
options( self , url , ** kwargs )
patch( self , url , data = None , ** kwargs )
post( self , url , data = None , json = None , ** kwargs )
prepare_request( self , request )
put( self , url , data = None , ** kwargs )
rebuild_auth( self , prepared_request , response )
rebuild_method( self , prepared_request , response )
rebuild_proxies( self , prepared_request , proxies )
request( self , method , url , params = None , data = None , headers = None , cookies = None , files = None , auth = None , timeout = None , allow_redirects = True , proxies = None , hooks = None , stream = None , verify = None , cert = None , json = None )
resolve_redirects( self , resp , req , stream = False , timeout = None , verify = True , cert = None , proxies = None , yield_requests = False , ** adapter_kwargs )
send( self , request , ** kwargs )
session( )
should_strip_auth( self , old_url , new_url )
```

## Notes

- `to_key_val_list(value)`: returns `None` for `None`; raises `ValueError` for `str`, `bytes`, `bool`, `int`;
  returns `list(value.items())` for a mapping; otherwise `list(value)`.
- `CaseInsensitiveDict` (from `.structures`): a mutable mapping whose key lookup is case-insensitive; it remembers the
  case of the last key set and preserves insertion order.
