You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `parse_header_links(value)`

## 1. Component overview

A helper in `requests.utils` that parses the value of an HTTP `Link` header
(RFC 5988 style), e.g.
`<http:/.../front.jpeg>; rel=front; type="image/jpeg",<http://.../back.jpeg>; rel=back;type="image/jpeg"`,
into a list of dictionaries, one per link. It is used by `Response.links`.
The parser is deliberately lenient and simple; its exact splitting rules
below define the expected output.

## 2. Functional requirements

Let *Q* be the character set `{' ', "'", '"'}` (space, single quote, double
quote).

1. Strip all leading and trailing characters in *Q* from the whole `value`.
   If the result is empty, return `[]`.
2. Split the stripped value into link entries at every occurrence of a comma
   followed by zero or more spaces and then `<` (the regular expression
   `', *<'`). The matched text (including the `<`) is removed. Commas not
   followed by optional spaces and `<` do not split (so a comma inside a
   parameter value such as `title="a, b"` is kept).
3. For each entry, in order:
   - Split it at the **first** `;` into a URL part and a parameter part. If
     there is no `;`, the whole entry is the URL part and there are no
     parameters.
   - The link's `'url'` is the URL part with all leading/trailing
     characters among `<`, `>`, space, `'` and `"` removed.
   - Split the parameter part on every `;` and process the pieces in order.
     Each piece must contain exactly one `=`; the text before it (stripped
     of *Q* characters) is the key and the text after it (stripped of *Q*
     characters) is the value, stored as `link[key] = value` (a repeated
     key overwrites the earlier value but keeps its original position).
     As soon as a piece does **not** contain exactly one `=` (no `=`, an
     empty piece, or two or more `=`), stop processing the remaining
     parameters of this link (they are ignored); the link itself is still
     kept.
4. Return the list of link dicts in entry order. Each dict has `'url'` as its
   first key, followed by the parameters in order of first appearance.

## 3. Input specification

- `value`: `str`, the raw header value (may be empty).

## 4. Output specification

A `list` of `dict`s mapping `str` to `str`.

| value | result |
|---|---|
| `'<http:/.../front.jpeg>; rel=front; type="image/jpeg"'` | `[{'url': 'http:/.../front.jpeg', 'rel': 'front', 'type': 'image/jpeg'}]` |
| `'<http:/.../front.jpeg>'` | `[{'url': 'http:/.../front.jpeg'}]` |
| `'<http:/.../front.jpeg>;'` | `[{'url': 'http:/.../front.jpeg'}]` |
| `'<http:/.../front.jpeg>; type="image/jpeg",<http://.../back.jpeg>;'` | `[{'url': 'http:/.../front.jpeg', 'type': 'image/jpeg'}, {'url': 'http://.../back.jpeg'}]` |
| `''` | `[]` |
| `'<a>; rel=x;; type=y'` | `[{'url': 'a', 'rel': 'x'}]` (empty piece stops parsing) |
| `'<a>; q=a=b; rel=x'` | `[{'url': 'a'}]` |
| `'<a>; rel=next,   <b>; rel=last'` | `[{'url': 'a', 'rel': 'next'}, {'url': 'b', 'rel': 'last'}]` |

## 5. Edge cases and constraints

- Keys and values may become empty strings after stripping
  (`'<a>; =x'` → `{'url': 'a', '': 'x'}`).
- Whitespace other than spaces (tabs, newlines) is not stripped.
- No URL validation or unquoting is performed.
- Pure function: no side effects; never raises for any `str` input.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `requests/utils.py`

## Imports / includes available in this file

```
import codecs
import contextlib
import io
import os
import re
import socket
import struct
import sys
import tempfile
import warnings
import zipfile
from .__version__ import __version__
from . import certs
from ._internal_utils import to_native_string
from .compat import parse_http_list as _parse_list_header
from .compat import (
    quote, urlparse, bytes, str, OrderedDict, unquote, getproxies,
    proxy_bypass, urlunparse, basestring, integer_types, is_py3,
    proxy_bypass_environment, getproxies_environment, Mapping)
from .cookies import cookiejar_from_dict
from .structures import CaseInsensitiveDict
from .exceptions import (
    InvalidURL, InvalidHeader, FileModeWarning, UnrewindableBodyError)
```

## Other functions defined in the same file (signatures only; you may call them)

```
_parse_content_type_header( header )
add_dict_to_cookiejar( cj , cookie_dict )
address_in_network( ip , net )
check_header_validity( header )
default_headers( )
default_user_agent( name = "python-requests" )
dict_from_cookiejar( cj )
dict_to_sequence( d )
dotted_netmask( mask )
extract_zipped_paths( path )
from_key_val_list( value )
get_auth_from_url( url )
get_encoding_from_headers( headers )
get_encodings_from_content( content )
get_environ_proxies( url , no_proxy = None )
get_netrc_auth( url , raise_errors = False )
get_unicode_from_response( r )
guess_filename( obj )
guess_json_utf( data )
is_ipv4_address( string_ip )
is_valid_cidr( string_network )
iter_slices( string , slice_length )
parse_dict_header( value )
parse_list_header( value )
prepend_scheme_if_needed( url , new_scheme )
proxy_bypass( host )
proxy_bypass_registry( host )
requote_uri( uri )
rewind_body( prepared_request )
select_proxy( url , proxies )
set_environ( env_name , value )
should_bypass_proxies( url , no_proxy )
stream_decode_response_unicode( iterator , r )
super_len( o )
to_key_val_list( value )
unquote_header_value( value , is_filename = False )
unquote_unreserved( uri )
urldefragauth( url )
```

=== STUB ===
```python
def parse_header_links(value):
    raise NotImplementedError  # TODO: implement according to the specification
```
