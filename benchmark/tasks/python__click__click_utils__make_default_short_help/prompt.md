You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `make_default_short_help(help, max_length=45)`

## 1. Component overview

`make_default_short_help` condenses a command's full help text into a one-line
summary. Click uses it when a command has no explicit `short_help`: the
summary is what appears next to the command name in the `Commands:` section of
a group's `--help` page and in shell-completion descriptions. The summary is
the leading part of the help text, cut at the end of the first sentence or at
a length limit, whichever comes first.

## 2. Functional requirements

1. Split `help` into words on any run of whitespace (spaces, tabs, newlines),
   exactly as `str.split()` with no arguments does. Leading/trailing
   whitespace and line breaks therefore disappear, and the words of the result
   are separated by single spaces.
2. Consume the words in order, building the summary:
   - The *cost* of adding a word is its length in characters, plus 1 for the
     separating space if the summary already contains at least one word.
   - If adding the word would make the summary length (sum of the costs of
     the words added so far) exceed `max_length`, append the literal `...`
     directly to the summary (no space before it) and stop. The word is not
     added.
   - Otherwise add the word (preceded by a single space unless it is the first
     word).
   - A word whose last character is `.` ends the first sentence: after it has
     been added, stop. (If such a word does not fit, the `...` rule above
     applies instead.)
3. Return the summary as a string. A summary length exactly equal to
   `max_length` is allowed (the limit is "not greater than").

Examples (with the default `max_length=45` unless stated):

- `'This is a short text.'` gives `'This is a short text.'`
- `'Login and store the token in ~/.netrc.'` gives
  `'Login and store the token in ~/.netrc.'`
- `'This is a long text that is too long to show as short help\n    and will be truncated instead.'`
  gives `'This is a long text that is too long to show...'` (the first 10 words
  take 44 characters; adding `as` would need 47). With `max_length=61` the
  same text gives `'This is a long text that is too long to show as short help...'`
  (58 characters; adding `and` would need 62).
- `'First sentence. Second sentence.'` gives `'First sentence.'`
- `'Show   the\n\tversion and exit'` gives `'Show the version and exit'`
- `'Supercalifragilistic word', max_length=10` gives `'...'`
  (the first word alone is too long).
- `'one two three', max_length=7` gives `'one two...'`
- `'one two three', max_length=13` gives `'one two three'`
- `'Use e.g. this'` gives `'Use e.g.'` (any word ending with a period ends
  the summary, even an abbreviation).
- `''` or `'   \n '` gives `''`.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `help` | `str` | The full help text; may be multi-line, may be empty. |
| `max_length` | `int` | Maximum number of characters of words and separating spaces in the summary, not counting a trailing `...`. Default `45`. Non-negative in practice. |

## 4. Output specification

A `str`: the condensed help. It contains whole words of `help` separated by
single spaces, optionally followed by `...` when truncation by length happened.
Because `...` is not counted, the result can be up to `max_length + 3`
characters long. The input string is not modified (strings are immutable).

## 5. Edge cases and constraints

- Empty or whitespace-only help gives the empty string.
- If the very first word is longer than `max_length`, the result is just `...`.
- Only the last character of a word is inspected for the sentence end; a word
  like `~/.netrc.` ends the sentence, while `v1.2` does not.
- When the sentence ends and the limit would be exceeded at the same word,
  the word is dropped and `...` is appended.
- If all words fit and none ends with `.`, the result is all words joined by
  single spaces with no ellipsis.
- Pure function: no I/O, no global state; thread-safe.

=== CONTEXT ===
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

=== STUB ===
```python
def make_default_short_help(help, max_length=45):
    raise NotImplementedError  # TODO: implement according to the specification
```
