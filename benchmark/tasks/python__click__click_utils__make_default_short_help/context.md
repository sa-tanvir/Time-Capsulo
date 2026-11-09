# Context for the function to implement

- **Language:** python
- **File:** `click/utils.py`

## Imports / includes available in this file

```
import os
import sys
from .globals import resolve_color_default
from ._compat import text_type, open_stream, get_filesystem_encoding, \
```

## Other functions defined in the same file (signatures only; you may call them)

```
_posixify( name )
close( self )
close_intelligently( self )
echo( message = None , file = None , nl = True , err = False , color = None )
flush( self )
format_filename( filename , shorten = False )
get_app_dir( app_name , roaming = True , force_posix = False )
get_binary_stream( name )
get_os_args( )
get_text_stream( name , encoding = None , errors = 'strict' )
make_str( value )
open( self )
open_file( filename , mode = 'r' , encoding = None , errors = 'strict' , lazy = False , atomic = False )
safecall( func )
safecall.wrapper( * args , ** kwargs )
```
