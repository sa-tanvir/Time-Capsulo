You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `merge_setting(request_setting, session_setting, dict_class=OrderedDict)`

## 1. Component overview

A module-level helper of `requests.sessions`. A `Session` carries default
settings (headers, query params, auth, proxies, `verify`, `stream`, `cert`,
hooks, ...), and each request may supply its own value for the same setting.
`merge_setting` decides the effective value: request values take precedence;
when both values are mappings they are merged key by key, and a request may
delete a session key by setting it to `None`. In a merged result, every key
whose value is `None` is dropped, whichever side (session or request) it
came from.

## 2. Functional requirements

1. If `session_setting` is `None`, return `request_setting` itself (the same
   object, which may also be `None`).
2. Otherwise, if `request_setting` is `None`, return `session_setting`
   itself (same object).
3. Otherwise, if either value is not a `Mapping` (`collections.abc.Mapping`,
   available as `Mapping`), return `request_setting` itself
   (e.g. `merge_setting(False, True)` → `False`;
   `merge_setting(('u', 'p'), {'a': 1})` → `('u', 'p')`).
4. Otherwise build a **new** mapping of type `dict_class`:
   - Start from the session's items, in the session mapping's iteration
     order.
   - Then apply the request's items, in its iteration order, as an update:
     keys already present get the request's value (keeping their original
     position for order-preserving classes); new keys are appended after
     the session keys.
   - Finally remove every key whose resulting value is `None`. This removes
     session entries that the request explicitly sets to `None`, and also
     `None`-valued entries coming from the session mapping itself.
   - Key equality is that of `dict_class`: with the default `OrderedDict`
     keys are case-sensitive (`{'foo': 'bar'}` from the session and
     `{'FOO': 'bar'}` from the request both survive), whereas with
     `dict_class=CaseInsensitiveDict` (used for headers) keys match
     case-insensitively and the request's spelling of a key wins
     (session `{'foo': 'bar'}`, request `{'FOO': None}` → empty result).
   - `dict_class` is called with a list of `(key, value)` pairs, and the
     result is updated with another list of pairs (both `dict`-like
     constructors/`update` accept that).
5. Return the merged mapping.

## 3. Input specification

- `request_setting`: any value or `None`; usually a mapping (headers,
  params, proxies, hooks) or a scalar (`bool`, tuple, string).
- `session_setting`: same kinds of values.
- `dict_class`: a mapping class constructible from a list of pairs and
  supporting `update`, `items` and `del` (default `OrderedDict`; also
  `CaseInsensitiveDict` or `dict`).

## 4. Output specification

Either one of the input objects unchanged (cases 1–3) or a new
`dict_class` instance (case 4).

Example (headers): session `OrderedDict(Accept-Encoding='identity',
First='1', Second='2')`, request `OrderedDict(Third='3', Fourth='4',
Fifth='5', Second='222')` with `dict_class=CaseInsensitiveDict` → items in
order: `Accept-Encoding: identity`, `First: 1`, `Second: 222`, `Third: 3`,
`Fourth: 4`, `Fifth: 5`.

Example (hooks): session `{'response': [h2]}`, request
`{'response': [h1]}` → `{'response': [h1]}` (values are replaced, not
combined).

Example: session `{'Accept-Encoding': None, 'X': '1'}`, request `{}` →
`{'X': '1'}`.

## 5. Edge cases and constraints

- Neither input is mutated.
- Values are not copied (the merged mapping holds the same value objects).
- Two empty mappings yield an empty `dict_class` instance.
- `to_key_val_list` (from `.utils`) converts a mapping into a list of its
  `(key, value)` items and may be used.

=== CONTEXT ===
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

=== STUB ===
```python
def merge_setting(request_setting, session_setting, dict_class=OrderedDict):
    raise NotImplementedError  # TODO: implement according to the specification
```
