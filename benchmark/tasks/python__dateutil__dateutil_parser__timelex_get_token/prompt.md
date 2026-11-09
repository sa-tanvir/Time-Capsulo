You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `_timelex.get_token(self)`

## 1. Component overview

`get_token` is the core of the lexer that `dateutil.parser` uses to split a free-form date/time
string (e.g. `"Thu Sep 25 10:36:28 BRST 2003"`, `"Sep.20.2009"`, `"4:30:21.447"`) into lexical
units. Each call returns the **next token** of the input stream as a `str`, or `None` once the
input is exhausted. Repeated calls (e.g. via `_timelex.split(s)`) therefore yield the complete
token sequence. Every token is a run of letters, a run of digits, a single whitespace marker, a
single punctuation character, or a number with a decimal separator. The difficulty is the dot
(and sometimes comma), which can be a field separator (`Sep.20.2009`) or a decimal point
(`21.447`, `28,123`).

## 2. Functional requirements

1. **Pending tokens first.** If earlier calls left tokens pending in `self.tokenstack`, remove and
   return the first one without reading any input.
2. **Reading characters.** Characters are taken first from `self.charstack` (front first), then
   from `self.instream.read(1)`. NUL characters (`'\x00'`) read from the stream are ignored
   entirely, as if absent (`"\x00a\x00b"` gives `['ab']`). When the stream returns `''`, set
   `self.eof = True`; the current token (if any) is finished. A character that ends a token but
   does not belong to it must not be lost: it is pushed onto `self.charstack` so the next call
   starts with it.
3. **First character of a token** decides its kind:
   - a whitespace character produces the token `' '` (a single space), whatever whitespace it was
     (tab, newline, ...). Each whitespace character is its own token: `" x\t\ny "` gives
     `[' ', 'x', ' ', ' ', 'y', ' ']`;
   - any other non-letter, non-digit character (`':'`, `'-'`, `','`, `'.'`, `'/'`, `'+'`, ...)
     is returned alone as a one-character token;
   - a letter starts a **word**, a digit starts a **number**.
4. **Words** extend over following letters. A digit or any other character ends the word
   (`"a1"` gives `['a', '1']`). A `'.'` after the word makes the chunk *dotted* (rule 6).
5. **Numbers** extend over following digits. A letter or other character ends the number
   (`"1a"` gives `['1', 'a']`). A `'.'` makes the chunk dotted; a `','` also does, but only when
   the number read so far has at least two digits (`"1,5"` gives `['1', ',', '5']`, while
   `"12,5"` is one chunk).
6. **Dotted chunks** keep growing while characters fit:
   - while the chunk is currently in a *letter phase* (it began as a word, or a letter was
     accepted last as described here), `'.'` and letters are accepted; a digit is accepted only if
     it immediately follows a `'.'`, and switches to a *digit phase*;
   - while in a *digit phase*, `'.'` and digits are accepted; a letter is accepted only if it
     immediately follows a `'.'`, and switches to a *letter phase*;
   - anything else (including `','`, whitespace, other punctuation, a letter/digit not directly
     after a `'.'`) ends the chunk and is kept for the next call.
7. **Breaking up dotted chunks.** A dotted chunk is broken up into pieces when **any** of these
   hold:
   - (a) letters were involved: the chunk started as a word, or, after switching to a letter
     phase, at least one more character was read from the input while in that phase (this
     includes the character that ended the chunk, but not the end of input);
   - (b) it contains more than one `'.'`;
   - (c) its last character is `'.'` or `','`.

   Breaking up means splitting at every `'.'` and `','`, keeping each separator as its own token
   and dropping empty pieces. The first piece is returned now; the remaining pieces are appended,
   in order, to `self.tokenstack` for subsequent calls.
8. **Decimal comma.** A chunk that started as a number, is not broken up, and contains no `'.'`
   (i.e. `<digits>,<digits>`) is returned with its comma replaced by `'.'`: `"28,123"` gives
   `'28.123'`.
9. Otherwise the accumulated chunk is returned unchanged.
10. When nothing remains (end of input reached, no pending characters or tokens), return `None`.
    Further calls keep returning `None`.

## 3. Input specification

- `self`: a `_timelex` instance whose `instream`, `charstack`, `tokenstack`, `eof` attributes are
  described in the context. The stream yields `str` characters (any Unicode).
- No arguments besides `self`.

## 4. Output specification

- A non-empty `str` token, or `None` at end of input.
- Side effects only on `self.charstack`, `self.tokenstack`, `self.eof` and the stream position.

Examples (token lists as produced by repeated calls, i.e. `_timelex.split(s)`):

| input | tokens |
|---|---|
| `"Thu Sep 25 10:36:28 BRST 2003"` | `Thu`,` `,`Sep`,` `,`25`,` `,`10`,`:`,`36`,`:`,`28`,` `,`BRST`,` `,`2003` |
| `"2003-09-25T10:49:41.5-03:00"` | `2003`,`-`,`09`,`-`,`25`,`T`,`10`,`:`,`49`,`:`,`41.5`,`-`,`03`,`:`,`00` |
| `"Sep.20.2009"` | `Sep`,`.`,`20`,`.`,`2009` |
| `"4:30:21.447"` | `4`,`:`,`30`,`:`,`21.447` |
| `"10:36:28,123"` | `10`,`:`,`36`,`:`,`28.123` |
| `"1999.12"` / `"0.5"` | `1999.12` / `0.5` |
| `"12.34.56"` | `12`,`.`,`34`,`.`,`56` |
| `"12."` / `"ab."` / `"12,"` | `12`,`.` / `ab`,`.` / `12`,`,` |
| `"3rd of May 2001"` | `3`,`rd`,` `,`of`,` `,`May`,` `,`2001` |
| `"July 4, 1976"` | `July`,` `,`4`,`,`,` `,`1976` |
| `"12,345"` / `"12,3,4"` | `12.345` / `12.3`,`,`,`4` |
| `"1,234.5"` | `1`,`,`,`234.5` |
| `"12,5.3"` | `12,5.3` (one dot, not broken up, comma kept) |
| `"5.6a"` / `"1.2a"` | `5.6`,`a` / `1.2`,`a` |
| `"a.1"` / `"x.12,5"` | `a`,`.`,`1` / `x`,`.`,`12`,`,`,`5` |
| `"3.c4"` | `3`,`.`,`c`,`4` |
| `"1.a"` (end of input right after `a`) | `1.a` |
| `"1.a "` / `"1.ab"` | `1`,`.`,`a`,` ` / `1`,`.`,`ab` |
| `"12,a"` | `12`,`,`,`a` |
| `"..."` / `"a..b"` | `.`,`.`,`.` / `a`,`.`,`.`,`b` |
| `""` | (none: first call returns `None`) |

## 5. Edge cases and constraints

- Never drop or duplicate input characters, except NULs (ignored) and whitespace (normalised to
  `' '`).
- A chunk never begins with `'.'` or `','`; a lone separator is a one-character token.
- The commas inside a broken-up chunk are separate tokens; rule 8 only applies to a chunk that
  was **not** broken up.
- Non-ASCII letters and digits follow `str.isalpha` / `str.isdigit` (`"é.ü"` gives `é`,`.`,`ü`).
- Must interoperate with the existing `__next__`, `split` and the attributes initialised by
  `__init__`; state left in `charstack`/`tokenstack` between calls must make subsequent calls
  continue the token sequence correctly.
- Not thread-safe (mutates the instance); runs in time linear in the input length.

=== CONTEXT ===
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

=== STUB ===
```python
def get_token(self):
    raise NotImplementedError  # TODO: implement according to the specification
```
