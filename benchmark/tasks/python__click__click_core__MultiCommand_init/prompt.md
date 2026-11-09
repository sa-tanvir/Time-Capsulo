You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `MultiCommand.__init__(self, name=None, invoke_without_command=False, no_args_is_help=None, subcommand_metavar=None, chain=False, result_callback=None, **attrs)`

## 1. Component overview

`click.MultiCommand` is the base class of commands that dispatch to
subcommands (`click.Group`, `click.CommandCollection` and the
`@click.group()` decorator build on it). Its constructor initialises a
multi command: everything a plain `click.Command` stores, plus the settings
that control how subcommands are dispatched, how the usage line names the
subcommand slot, and whether several subcommands may be chained. It also
validates that a chaining multi command has no optional positional
arguments. Subclasses call it as `MultiCommand.__init__(self, name, **attrs)`.

## 2. Functional requirements

1. **Base initialisation.** Initialise the object as a `Command` with
   `name` and all remaining keyword arguments `**attrs` (e.g. `params`,
   `callback`, `help`, `short_help`, `epilog`, `hidden`, `deprecated`,
   `context_settings`, `options_metavar`, `add_help_option`). Afterwards
   `self.name`, `self.params` (a list, `[]` when not given), `self.help`,
   `self.callback`, etc. behave exactly as for a plain `Command`; unknown
   keyword arguments raise the same `TypeError` that `Command.__init__`
   would raise.
2. Set these instance attributes:
   - `invoke_without_command`: the argument as given (default `False`).
     When false, the group's own callback only runs if a subcommand is
     given.
   - `no_args_is_help`: the argument if it is not `None`; otherwise
     `not invoke_without_command` (so by default calling a group with no
     arguments shows its help, but a group created with
     `invoke_without_command=True` runs its callback instead).
   - `subcommand_metavar`: the argument if it is not `None`; otherwise
     `'COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...'` when `chain` is truthy,
     else `'COMMAND [ARGS]...'` (the module constants `SUBCOMMANDS_METAVAR`
     and `SUBCOMMAND_METAVAR`). This string appears in the usage line, e.g.
     `Usage: cli [OPTIONS] COMMAND [ARGS]...`, or for a chaining group
     `Usage: cli [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...`.
   - `chain`: the argument as given.
   - `result_callback`: the argument as given (default `None`); it can later
     be replaced through the `resultcallback()` decorator.
3. **Chain validation.** If `chain` is truthy, inspect the command's
   parameters (`self.params`, after base initialisation): if any of them is a
   `click.Argument` whose `required` attribute is false, raise
   `RuntimeError('Multi commands in chain mode cannot have optional
   arguments.')`. Options are never a problem; required arguments are
   allowed. Note that an argument declared with `nargs=-1` and no explicit
   `required=True` is not required, so it is also rejected. Example:
   `@click.group(chain=True)` with `@click.argument('forbidden',
   required=False)` (or `nargs=-1`) raises `RuntimeError` at definition
   time, while `@click.group(chain=True)` with `@click.argument('arg')`
   works (`cli foo a` runs the group with `arg='foo'`, then subcommand `a`).
4. Returns `None`.

## 3. Input specification

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` or `None` | Command name. |
| `invoke_without_command` | `bool` | Run the group callback even without a subcommand. |
| `no_args_is_help` | `bool` or `None` | Show help when called with no arguments; `None` = derive. |
| `subcommand_metavar` | `str` or `None` | Usage-line text for the subcommand slot; `None` = derive. |
| `chain` | `bool` | Allow several subcommands in one invocation. |
| `result_callback` | callable or `None` | Called with the subcommand results. |
| `**attrs` | keyword args | Forwarded to `Command.__init__`. |

## 4. Output specification

No return value. The instance carries the `Command` attributes plus
`no_args_is_help`, `invoke_without_command`, `subcommand_metavar`, `chain`
and `result_callback` as described; class attributes
`allow_extra_args = True` and `allow_interspersed_args = False` remain
inherited from the class. On an invalid chain configuration a
`RuntimeError` with the exact message above is raised.

## 5. Edge cases and constraints

- Explicit `no_args_is_help=False` / `subcommand_metavar=''` are kept
  as given (only `None` triggers the defaults).
- With `chain=False` no parameter is inspected, so optional arguments are
  fine.
- The `params` list passed in is used as the command's parameter list;
  it is not copied or modified.

=== CONTEXT ===
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


## Module constants and other members of the enclosing class `MultiCommand` and its bases (you may rely on them)

```
SUBCOMMAND_METAVAR = 'COMMAND [ARGS]...'
SUBCOMMANDS_METAVAR = 'COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...'


class BaseCommand(object):
    def __init__(self, name, context_settings=None): ...


class Command(BaseCommand):
    def __init__(self, name, context_settings=None, callback=None,
                 params=None, help=None, epilog=None, short_help=None,
                 options_metavar='[OPTIONS]', add_help_option=True,
                 hidden=False, deprecated=False):
        # stores all of these; self.params becomes `params or []`
        ...


class Argument(Parameter):
    # positional parameter; `required` defaults to False when a default is given
    # or when nargs <= 0 (e.g. nargs=-1), True otherwise
    ...


class MultiCommand(Command):
    allow_extra_args = True
    allow_interspersed_args = False
    ...
```

=== STUB ===
```python
def __init__(self, name=None, invoke_without_command=False,
             no_args_is_help=None, subcommand_metavar=None,
             chain=False, result_callback=None, **attrs):
    raise NotImplementedError  # TODO: implement according to the specification
```
