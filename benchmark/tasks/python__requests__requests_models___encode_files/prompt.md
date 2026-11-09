You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `RequestEncodingMixin._encode_files(files, data)`

## 1. Component overview

A static method of `RequestEncodingMixin` (mixed into `PreparedRequest` of the
`requests` HTTP library). It builds a `multipart/form-data` request body from
ordinary form fields (`data`) and file uploads (`files`), and returns the body
together with the matching `Content-Type` header value. The actual multipart
serialisation is delegated to urllib3 (`RequestField`,
`encode_multipart_formdata`, both imported in this module).

## 2. Functional requirements

1. **Validation.**
   - If `files` is falsy (`None`, `{}`, `[]`), raise
     `ValueError("Files must be provided.")`.
   - Else, if `data` is a `str` or `bytes`, raise
     `ValueError("Data must not be a string.")`.
2. **Normalise containers.** Both `data` (or `{}` if `data` is falsy) and
   `files` are turned into ordered lists of `(name, value)` pairs with
   `to_key_val_list` (mappings in iteration order, sequences of pairs in
   their order). An element of `files` that is not a 2-item pair (e.g.
   `files=['bad file data']`) causes a `ValueError` during unpacking.
3. **Plain form fields come first**, in order. For each `(field, val)` of
   `data`:
   - If `val` is a `str`/`bytes` or is not iterable, it is a single value;
     otherwise (list, tuple, ...) each element is a separate value for the
     same field name, in order.
   - `None` values are skipped.
   - A value that is not `bytes` is converted with `str()` first; then `str`
     values are UTF-8 encoded, so every emitted value is `bytes`.
   - A field name given as `bytes` is decoded from UTF-8 to `str`
     (`{b'stuff': 'elixr'}` yields a part named `stuff`, not `b'stuff'`).
   - Each value becomes one simple multipart part, given to
     `encode_multipart_formdata` as a `(name, value_bytes)` tuple (part with
     only a `Content-Disposition: form-data; name="..."` header).
4. **File parts follow**, in order. For each `(k, v)` of `files`:
   - If `v` is a `tuple` or `list`, it is `(filename, fileobj)`,
     `(filename, fileobj, content_type)` or
     `(filename, fileobj, content_type, custom_headers)`; missing items
     default to `None`.
   - Otherwise `v` itself is the file object/content and the filename is
     `guess_filename(v)`, or the key `k` if that gives nothing (e.g. an
     object without a usable `name`, or whose `name` is not a string).
   - Content of the part: if the file object is `str`, `bytes` or
     `bytearray`, it is used directly; if it has a `read` attribute, the
     result of calling `read()` once is used; if it is `None`, the entry is
     skipped entirely (no part at all); any other object (e.g. an `int`) is
     used as-is.
   - Each part is a urllib3 `RequestField` with name `k`, that content, the
     filename and the custom headers, made multipart with the given content
     type (so the part carries `Content-Disposition: form-data; name="k";
     filename="..."` and, when a content type was given, a `Content-Type`
     header, e.g. `text/py-content-type`).
5. **Encode** all parts (form fields first, then files) with
   `encode_multipart_formdata` and return its `(body, content_type)` result.

## 3. Input specification

- `files`: a mapping or a sequence of `(name, value)` pairs. `value` is a
  file-like object, `str`/`bytes`/`bytearray` content, `None`, another
  object, or a 2/3/4-tuple/list as described above. Names are `str`.
- `data`: `None`, a mapping or sequence of `(name, value)` pairs (names
  `str` or `bytes`; values `str`, `bytes`, numbers, `None` or lists of
  these). Must not be a `str`/`bytes`.

## 4. Output specification

A 2-tuple `(body, content_type)`:
- `body`: `bytes`, the complete multipart body.
- `content_type`: `str` of the form
  `'multipart/form-data; boundary=<boundary>'`. The boundary is randomly
  chosen by urllib3; callers must not rely on its value.

Example: `files={'file': ('report.csv', b'a,b\n', 'text/csv')}`,
`data={'k': ['1', 2], 'skip': None}` produces a body with three parts in
order: `name="k"` / `1`, `name="k"` / `2`, then
`name="file"; filename="report.csv"` with `Content-Type: text/csv` and
content `a,b\n`.

`files={"random-file-1": None, "random-file-2": 1}`: the body has no part
named `random-file-1` and one part named `random-file-2` (filename
`random-file-2`, content `1`).

## 5. Edge cases and constraints

- File-like objects are read (consumed) exactly once; nothing else is
  mutated.
- A file object whose `name` attribute is a non-string (e.g. `2`) or looks
  like `<stdin>` falls back to the key as filename.
- Field values given as `bytes` are passed through without re-encoding.
- Errors: only the two `ValueError`s above plus whatever unpacking or
  urllib3 raises for malformed inputs.

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

## Notes

- This is a `@staticmethod` of `class RequestEncodingMixin` (the decorator stays in place above the stub); it has no
  instance state.
- `basestring` from `.compat` is `(str, bytes)` on Python 3.
- `to_key_val_list(value)`: returns `None` for `None`; raises `ValueError` for `str`, `bytes`, `bool`, `int`;
  returns `list(value.items())` for a mapping; otherwise `list(value)`.
- `guess_filename(obj)`: returns `os.path.basename(obj.name)` when `obj.name` is a non-empty string that does not
  start with `<` or end with `>`; otherwise `None`.
- urllib3 (1.25): `RequestField(name, data, filename=None, headers=None)`; `RequestField.make_multipart(content_disposition=None, content_type=None, content_location=None)`;
  `encode_multipart_formdata(fields, boundary=None)` accepts `RequestField` objects and `(name, data)` tuples and
  returns `(body_bytes, content_type_str)`.

=== STUB ===
```python
def _encode_files(files, data):
    raise NotImplementedError  # TODO: implement according to the specification
```
