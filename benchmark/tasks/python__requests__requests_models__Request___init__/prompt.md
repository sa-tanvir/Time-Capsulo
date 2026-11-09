You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Request.__init__(self, method=None, url=None, headers=None, files=None, data=None, params=None, auth=None, cookies=None, hooks=None, json=None)`

## 1. Component overview

The constructor of `requests.Request`, the user-facing, not-yet-prepared
description of an HTTP request. It stores the given request components as
attributes, substituting empty containers for omitted ones, and registers
any supplied event hooks. `Request.prepare()` and `Session.prepare_request()`
later read these attributes.

## 2. Functional requirements

1. Store the arguments on the instance under the same names:
   `self.method`, `self.url`, `self.headers`, `self.files`, `self.data`,
   `self.json`, `self.params`, `self.auth`, `self.cookies`.
   - The objects passed in are stored as-is (no copying, no validation, no
     normalisation): e.g. `self.headers is headers` when a headers dict is
     given, and a `bytes` URL stays `bytes`.
   - Defaults when the argument is `None`: `data` → a new empty list `[]`,
     `files` → a new empty list `[]`, `headers` → a new empty dict `{}`,
     `params` → a new empty dict `{}`. Each instance gets its own fresh
     containers. `method`, `url`, `json`, `auth` and `cookies` stay `None`
     when not given.
   - Only `None` triggers a default; other falsy values (e.g. `{}`, `''`)
     are stored unchanged.
2. Hooks:
   - `self.hooks` is always a **new** dict created with `default_hooks()`,
     i.e. `{'response': []}` (one empty list per supported event).
   - If `hooks` is given (a mapping of event name → hook or iterable of
     hooks), each `(event, hook)` item is registered, in the mapping's
     iteration order, through `self.register_hook(event=event, hook=hook)`:
     - a callable is appended to `self.hooks[event]`;
     - an iterable is expanded and its callable elements appended in order
       (non-callables are silently skipped);
     - an event name that is not supported raises
       `ValueError('Unsupported event specified, with event name "<event>"')`.
   - The caller's `hooks` mapping and lists are never stored or mutated:
     `Request(hooks=h).hooks is not h`, and `self.hooks['response']` is a
     different list from any list in `h`.
3. Returns `None` (constructor).

## 3. Input specification

All parameters are optional:
- `method`: `str` (e.g. `'GET'`) or `None`.
- `url`: `str`/`bytes` or `None`.
- `headers`: mapping or `None`.
- `files`, `data`: mapping / list of tuples / `str` / `bytes` / file-like,
  or `None`.
- `params`: mapping, list of tuples, `str`/`bytes`, or `None`.
- `auth`: tuple or auth callable, or `None`.
- `cookies`: dict or `CookieJar`, or `None`.
- `hooks`: mapping of event name to a callable or an iterable of callables,
  or `None`.
- `json`: any JSON-serialisable object or `None`.

## 4. Output specification

No return value; the instance attributes described above are set.

Examples:
- `Request()` → `method=None, url=None, headers={}, files=[], data=[],
  json=None, params={}, auth=None, cookies=None, hooks={'response': []}`.
- `Request('GET', 'http://x/', hooks={'response': h})` →
  `hooks == {'response': [h]}`.
- `Request(hooks={'response': [h1, 'not callable', h2]})` →
  `hooks == {'response': [h1, h2]}`.
- `Request(hooks={'response': []})` → `hooks == {'response': []}`.
- `Request(hooks={'request': h})` → `ValueError`.

## 5. Edge cases and constraints

- The instance must remain picklable (attributes are plain stored objects).
- Registering happens after `self.hooks` has been initialised; other
  attributes may be set before or after hook registration, but if
  registration raises, the exception propagates.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `requests/models.py`
- **Enclosing scope:** `class Request(RequestHooksMixin)`

## Imports / includes available in this file

```
import datetime
import sys
import encodings.idna
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata
from urllib3.util import parse_url
from urllib3.exceptions import (
    DecodeError, ReadTimeoutError, ProtocolError, LocationParseError)
from io import UnsupportedOperation
from .hooks import default_hooks
from .structures import CaseInsensitiveDict
from .auth import HTTPBasicAuth
from .cookies import cookiejar_from_dict, get_cookie_header, _copy_cookie_jar
from .exceptions import (
    HTTPError, MissingSchema, InvalidURL, ChunkedEncodingError,
    ContentDecodingError, ConnectionError, StreamConsumedError)
from ._internal_utils import to_native_string, unicode_is_ascii
from .utils import (
    guess_filename, get_auth_from_url, requote_uri,
    stream_decode_response_unicode, to_key_val_list, parse_header_links,
    iter_slices, guess_json_utf, super_len, check_header_validity)
from .compat import (
    Callable, Mapping,
    cookielib, urlunparse, urlsplit, urlencode, str, bytes,
    is_py2, chardet, builtin_str, basestring)
from .compat import json as complexjson
from .status_codes import codes
```

## Other functions defined in the same file (signatures only; you may call them)

```
_encode_files( files , data )
_encode_params( data )
_get_idna_encoded_host( host )
apparent_encoding( self )
close( self )
content( self )
copy( self )
deregister_hook( self , event , hook )
is_permanent_redirect( self )
is_redirect( self )
iter_content( self , chunk_size = 1 , decode_unicode = False )
iter_content.generate( )
iter_lines( self , chunk_size = ITER_CHUNK_SIZE , decode_unicode = False , delimiter = None )
json( self , ** kwargs )
links( self )
next( self )
ok( self )
path_url( self )
prepare( self )
prepare( self , method = None , url = None , headers = None , files = None , data = None , params = None , auth = None , cookies = None , hooks = None , json = None )
prepare_auth( self , auth , url = '' )
prepare_body( self , data , files , json = None )
prepare_content_length( self , body )
prepare_cookies( self , cookies )
prepare_headers( self , headers )
prepare_hooks( self , hooks )
prepare_method( self , method )
prepare_url( self , url , params )
raise_for_status( self )
register_hook( self , event , hook )
text( self )
```

## Instance state

- Attributes written by the constructor: `method`, `url`, `headers`, `files`, `data`, `json`, `params`, `auth`,
  `cookies`, `hooks` (no others).
- `default_hooks()` (from `.hooks`) returns a new dict `{'response': []}` with one empty list per supported event
  (`HOOKS = ['response']`).
- `register_hook(self, event, hook)` (inherited from `RequestHooksMixin`): raises
  `ValueError('Unsupported event specified, with event name "%s"' % event)` if `event` is not a key of `self.hooks`;
  appends `hook` to `self.hooks[event]` if it is callable; otherwise, if `hook` is iterable, extends
  `self.hooks[event]` with its callable elements.

=== STUB ===
```python
def __init__(self,
        method=None, url=None, headers=None, files=None, data=None,
        params=None, auth=None, cookies=None, hooks=None, json=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
