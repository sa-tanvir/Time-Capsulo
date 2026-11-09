# Context for the function to implement

- **Language:** python
- **File:** `dateutil/parser/_parser.py`
- **Enclosing scope:** `class _timelex(object)`

## Imports / includes available in this file

```
from __future__ import unicode_literals
import datetime
import re
import string
import time
import warnings
from calendar import monthrange
from io import StringIO
import six
from six import integer_types, text_type
from decimal import Decimal
from warnings import warn
from .. import relativedelta
from .. import tz
```

## Other functions defined in the same file (signatures only; you may call them)

```
_adjust_ampm( self , hour , ampm )
_ampm_valid( self , hour , ampm , fuzzy )
_assign_hms( self , res , value_repr , hms )
_assign_tzname( self , dt , tzname )
_build_naive( self , res , default )
_build_tzaware( self , naive , res , tzinfos )
_build_tzinfo( self , tzinfos , tzname , tzoffset )
_convert( self , lst )
_could_be_tzname( self , hour , tzname , tzoffset , token )
_find_hms_idx( self , idx , tokens , info , allow_jump )
_parse( self , timestr , dayfirst = None , yearfirst = None , fuzzy = False , fuzzy_with_tokens = False )
_parse_hms( self , idx , tokens , info , hms_idx )
_parse_min_sec( self , value )
_parse_numeric_token( self , tokens , idx , info , ymd , res , fuzzy )
_parsems( self , value )
_parsetz( tzstr )
_recombine_skipped( self , tokens , skipped_idxs )
_repr( self , classname )
_resolve_from_stridxs( self , strids )
_to_decimal( self , val )
ampm( self , name )
append( self , val , label = None )
convertyear( self , year , century_specified = False )
could_be_day( self , value )
has_day( self )
has_month( self )
has_year( self )
hms( self , name )
isnum( cls , nextchar )
isspace( cls , nextchar )
isword( cls , nextchar )
jump( self , name )
month( self , name )
next( self )
parse( self , timestr , default = None , ignoretz = False , tzinfos = None , ** kwargs )
parse( self , tzstr )
parse( timestr , parserinfo = None , ** kwargs )
pertain( self , name )
resolve_ymd( self , yearfirst , dayfirst )
split( cls , s )
tzoffset( self , name )
utczone( self , name )
validate( self , res )
weekday( self , name )
```

## Instance state and other members of the enclosing class (you may rely on them)

`_timelex` is the lexer used by `dateutil.parser` to break a date/time string into tokens. The
method to implement, `get_token(self)`, is called repeatedly; each call returns the next token.

```
class _timelex(object):
    # Fractional seconds are sometimes split by a comma
    _split_decimal = re.compile("([.,])")      # class attribute

    def __init__(self, instream):
        # bytes-like input is decoded first; a str is wrapped in io.StringIO;
        # anything else must have a .read() method (otherwise TypeError)
        self.instream = instream    # text stream; read one character at a time with self.instream.read(1)
                                    # (returns '' at end of input)
        self.charstack = []         # list[str]: single characters that were read from the stream but
                                    # not yet consumed; they must be consumed (from the front) before
                                    # reading any more from instream
        self.tokenstack = []        # list[str]: tokens already produced but not yet returned; returned
                                    # (from the front) by subsequent get_token() calls
        self.eof = False            # bool: set to True once instream reported end of input

    def __iter__(self): return self
    def __next__(self):             # calls get_token(); raises StopIteration when it returns None
    def next(self):                 # Python 2 alias of __next__

    @classmethod
    def split(cls, s):              # list(cls(s)): the full token list of s

    @classmethod
    def isword(cls, nextchar):      # nextchar.isalpha()
    @classmethod
    def isnum(cls, nextchar):       # nextchar.isdigit()
    @classmethod
    def isspace(cls, nextchar):     # nextchar.isspace()
```

Throughout the specification, "letter", "digit" and "whitespace" mean exactly what `isword`,
`isnum` and `isspace` return True for.
