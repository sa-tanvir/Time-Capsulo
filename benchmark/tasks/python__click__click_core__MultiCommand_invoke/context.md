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
format_commands( self , ctx , formatter )
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


## Other members of the enclosing class `MultiCommand`, its bases and `Context` (you may rely on them)

```
class Context(object):
    # selected attributes
    #   protected_args: list  - leading leftover args that must not be consumed by the parent
    #                           (for a multi command: the subcommand name, or in chain mode all leftovers)
    #   args: list            - other leftover args
    #   params: dict          - the parsed parameter values of this command
    #   invoked_subcommand    - None by default
    #   obj                   - user object, inherited by child contexts when they are created

    def __enter__(self): ...   # pushes the context; contexts may be entered several times
    def __exit__(self, exc_type, exc_value, tb): ...   # runs close callbacks when the outermost `with` ends

    def fail(self, message):
        raise UsageError(message, self)

    def invoke(*args, **kwargs):
        """ctx.invoke(callback, *args, **kwargs): calls `callback` in the context (with usage-error
        augmentation) and returns its result."""


class Command(BaseCommand):
    def make_context(self, info_name, args, parent=None, **extra):
        """Creates a new Context(self, info_name=info_name, parent=parent, **extra), parses `args`
        into it and returns it (does not invoke the callback). Parsing errors raise UsageError;
        `--help` prints help and exits."""

    def invoke(self, ctx):
        """Invokes the attached callback (if any) as ctx.invoke(self.callback, **ctx.params)."""


class MultiCommand(Command):
    # set by __init__: invoke_without_command, chain, result_callback, no_args_is_help, subcommand_metavar

    def parse_args(self, ctx, args):
        # after parsing the multi command's own parameters, the leftover args are stored as:
        #   chain mode:     ctx.protected_args = leftovers, ctx.args = []
        #   non-chain mode: ctx.protected_args = leftovers[:1], ctx.args = leftovers[1:] (if any)
        ...

    def resolve_command(self, ctx, args):
        """Looks up the subcommand named by args[0] (honouring ctx.token_normalize_func) and returns
        (cmd_name, cmd, args[1:]). Fails with UsageError 'No such command "<name>".' if unknown."""
```
