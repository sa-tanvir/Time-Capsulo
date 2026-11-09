You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `RequestEncodingMixin._encode_params(data)`

## 1. Component overview

A static method of `RequestEncodingMixin` (mixed into `PreparedRequest` in the
`requests` HTTP library). It turns request parameters or form data into an
`application/x-www-form-urlencoded` string, used both for URL query strings
and for form-encoded request bodies. Values that are already "raw" are passed
through untouched.

## 2. Functional requirements

1. If `data` is a `str` or `bytes`, return it unchanged (same object).
2. Else, if `data` has a `read` attribute (file-like), return it unchanged.
3. Else, if `data` is iterable (has `__iter__`, e.g. a `dict`, `OrderedDict`,
   other mapping, `list` or `tuple` of 2-item pairs), convert it to a list of
   `(key, value)` pairs with `to_key_val_list(data)` (mappings contribute their
   items in iteration order; sequences of pairs keep their order) and:
   - A value that is a `str`/`bytes`, or that is not iterable (int, float,
     `None`, ...), is treated as a single value. Any other iterable value
     (list, tuple, ...) is treated as a sequence of values for the same key,
     producing one `key=value` entry per element, in order.
   - Individual values that are `None` are dropped (a key whose only value is
     `None`, or whose value list is empty, does not appear at all).
   - Keys and values that are `str` are UTF-8 encoded before quoting; `bytes`
     are used as-is; other objects (numbers, ...) are converted with `str()`.
   - The result is exactly what the standard library's
     `urlencode(pairs, doseq=True)` produces for the flattened, encoded list
     of pairs: entries joined by `&`, key and value joined by `=`, quoted with
     `quote_plus` rules (space → `+`, reserved and non-ASCII bytes →
     upper-case `%XX`, letters, digits and `_.-~` kept).
4. Otherwise (any non-iterable object such as an `int`), return `data`
   unchanged.

## 3. Input specification

- `data`: `str`, `bytes`, a file-like object, a mapping, an iterable of
  2-item `(key, value)` sequences, `None`, or any other object.
- Keys: `str` or `bytes` (or other objects accepted by `urlencode`).
- Values: `str`, `bytes`, numbers, `None`, or lists/tuples of these.

## 4. Output specification

- For iterable input: a `str` (possibly empty `''`).
- Otherwise the input object itself.

Examples:

| data | result |
|---|---|
| `{'life': '42'}` | `'life=42'` |
| `{'test': ['foo', 'baz']}` | `'test=foo&test=baz'` |
| `(('a', 'b'), ('c', 'd'))` | `'a=b&c=d'` |
| `OrderedDict([('z', 1), ('a', 1), ('k', 1), ('d', 1)])` | `'z=1&a=1&k=1&d=1'` |
| `{'foo': 'føø'}` | `'foo=f%C3%B8%C3%B8'` |
| `{'a': 'x y', 'b': None}` | `'a=x+y'` |
| `{b'k': b'v&w'}` | `'k=v%26w'` |
| `[('k', [1, None, 'x'])]` | `'k=1&k=x'` |
| `'already=encoded'` / `b'raw'` | returned unchanged |
| `None` | `None` |
| `{}` / `[]` | `''` |

## 5. Edge cases and constraints

- Must not mutate `data`.
- The output for a list/tuple of pairs is equal to the standard
  `urlencode(data)` when all keys and values are plain ASCII strings
  (tests compare against it).
- A sequence element that is not a 2-item pair makes unpacking fail with
  `ValueError`; no special handling is required.
- Order of the output entries follows the input order exactly.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `requests/models.py`
- **Enclosing scope:** `class RequestEncodingMixin(object)`

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

## Notes

- This is a `@staticmethod` of `class RequestEncodingMixin` (the decorator stays in place above the stub); it has no
  instance state.
- `basestring` from `.compat` is `(str, bytes)` on Python 3; `str` and `bytes` are the builtins.
- `to_key_val_list(value)`: returns `None` for `None`; raises `ValueError` for `str`, `bytes`, `bool`, `int`;
  returns `list(value.items())` for a mapping; otherwise `list(value)`.

=== STUB ===
```python
def _encode_params(data):
    raise NotImplementedError  # TODO: implement according to the specification
```
