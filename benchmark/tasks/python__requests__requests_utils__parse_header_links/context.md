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
