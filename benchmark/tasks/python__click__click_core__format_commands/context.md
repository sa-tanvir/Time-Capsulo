# Context for the function to implement

- **Language:** python
- **File:** `click/core.py`
- **Enclosing scope:** `class MultiCommand(Command)`

## Imports / includes available in this file

```
import errno
import inspect
import os
import sys
from contextlib import contextmanager
from itertools import repeat
from functools import update_wrapper
from .types import convert_type, IntRange, BOOL
from .utils import PacifyFlushWrapper, make_str, make_default_short_help, \
from .exceptions import ClickException, UsageError, BadParameter, Abort, \
from .termui import prompt, confirm, style
from .formatting import HelpFormatter, join_options
from .parser import OptionParser, split_opt
from .globals import push_context, pop_context
from ._compat import PY2, isidentifier, iteritems, string_types
from ._unicodefun import _check_for_unicode_literals, _verify_python3_env
from .decorators import command, group
```

## Other functions defined in the same file (signatures only; you may call them)

```
_bashcomplete( cmd , prog_name , complete_var = None )
_check_multicommand( base_command , cmd_name , cmd , register = False )
_maybe_show_deprecated_notice( cmd )
_parse_decls( self , decls , expose_value )
abort( self )
add_command( self , cmd , name = None )
add_source( self , multi_cmd )
add_to_parser( self , parser , ctx )
augment_usage_errors( ctx , param = None )
batch( iterable , batch_size )
call_on_close( self , f )
close( self )
collect_usage_pieces( self , ctx )
command( self , * args , ** kwargs )
command.decorator( f )
command_path( self )
consume_value( self , ctx , opts )
ensure_object( self , object_type )
exit( self , code = 0 )
fail( self , message )
fast_exit( code )
find_object( self , object_type )
find_root( self )
format_epilog( self , ctx , formatter )
format_help( self , ctx , formatter )
format_help_text( self , ctx , formatter )
format_options( self , ctx , formatter )
format_usage( self , ctx , formatter )
forward( * args , ** kwargs )
full_process_value( self , ctx , value )
get_command( self , ctx , cmd_name )
get_default( self , ctx )
get_error_hint( self , ctx )
get_help( self )
get_help( self , ctx )
get_help_option( self , ctx )
get_help_option.show_help( ctx , param , value )
get_help_option_names( self , ctx )
get_help_record( self , ctx )
get_help_record._write_opts( opts )
get_params( self , ctx )
get_short_help_str( self , limit = 45 )
get_usage( self )
get_usage( self , ctx )
get_usage_pieces( self , ctx )
group( self , * args , ** kwargs )
group.decorator( f )
handle_parse_result( self , ctx , opts , args )
human_readable_name( self )
invoke( * args , ** kwargs )
invoke( self , ctx )
invoke._process_result( value )
invoke_param_callback( callback , ctx , param , value )
iter_params_for_processing( invocation_order , declaration_order )
iter_params_for_processing.sort_key( item )
list_commands( self , ctx )
lookup_default( self , name )
main( self , args = None , prog_name = None , complete_var = None , standalone_mode = True , ** extra )
make_context( self , info_name , args , parent = None , ** extra )
make_formatter( self )
make_metavar( self )
make_parser( self , ctx )
meta( self )
parse_args( self , ctx , args )
process_value( self , ctx , value )
prompt_for_value( self , ctx )
resolve_command( self , ctx , args )
resolve_envvar_value( self , ctx )
resultcallback( self , replace = False )
resultcallback.decorator( f )
resultcallback.resultcallback.decorator.function( __value , * args , ** kwargs )
scope( self , cleanup = True )
type_cast_value( self , ctx , value )
type_cast_value._convert( value , level )
value_from_envvar( self , ctx )
value_is_missing( self , value )
```

## Instance state and collaborators

`format_commands` is a method of `MultiCommand` (base class of `Group` and `CommandCollection`).
It reads no instance attributes directly; it relies on these members:

```
class MultiCommand(Command):
    def list_commands(self, ctx):
        """Returns a list of subcommand names in the order they should appear.
        (Group: sorted(self.commands); subclasses may return any names.)"""

    def get_command(self, ctx, cmd_name):
        """Returns the Command object for cmd_name, or None if it does not exist."""


class BaseCommand / Command:
    name: str           # the command's own name (may differ from the name it is registered under)
    hidden: bool        # True -> the command must not be listed in help output
    short_help: str     # explicit short help or None
    help: str           # full help text or None

    def get_short_help_str(self, limit=45):
        """Returns self.short_help if set, otherwise the help text condensed to at most
        `limit` characters (plus a possible '...'), or '' if there is no help."""


class HelpFormatter(object):          # from click.formatting
    width: int                        # total output width in columns

    def section(self, name):
        """Context manager: writes a paragraph break and the heading '<name>:',
        and indents everything written inside the `with` block."""

    def write_dl(self, rows, col_max=30, col_spacing=2):
        """Writes a two-column definition list; rows is a list of (term, description) tuples."""
```
