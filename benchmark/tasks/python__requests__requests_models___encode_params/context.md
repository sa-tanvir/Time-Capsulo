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
