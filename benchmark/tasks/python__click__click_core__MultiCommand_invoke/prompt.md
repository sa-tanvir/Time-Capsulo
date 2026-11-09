You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `MultiCommand.invoke(self, ctx)`

## 1. Component overview

`click.MultiCommand` (base of `click.Group`) is a command that dispatches to
subcommands. After the multi command's own parameters have been parsed into
`ctx` (see `parse_args` in `context.md`: the leftover arguments — the
subcommand name(s) and their arguments — are kept in `ctx.protected_args`
and `ctx.args`), `invoke` runs the multi command's own callback, resolves and
parses the subcommand(s), invokes them, and optionally passes their results
through the multi command's result callback. It supports a normal mode
(exactly one subcommand) and a *chain* mode (`self.chain`, any number of
subcommands one after the other, e.g. `cli bdist --format=1 sdist 2`).

## 2. Functional requirements

Let *process(value)* mean: if the multi command has a result callback
(`result_callback` attribute not `None`), call it via the context's `invoke`
helper with `value` as its only positional argument and the multi command's
own parsed parameters (the entries of `ctx.params`) as keyword arguments, and
return what it returns; otherwise return `value` unchanged.

1. **No subcommand given** (`ctx.protected_args` is empty):
   - If `self.invoke_without_command` is false: fail with
     `ctx.fail('Missing command.')` (a `click.UsageError`; shown as
     `Error: Missing command.`, exit code 2).
   - If true and not in chain mode: run the multi command's own callback
     (as `Command.invoke(self, ctx)` does) and return its return value; the
     result callback is **not** applied. `ctx.invoked_subcommand` stays
     `None`.
   - If true and in chain mode: inside the context (`with ctx:`), run the
     own callback, then return *process(`[]`)*.
2. **Subcommand(s) given:** take the full list of leftover arguments
   `ctx.protected_args + ctx.args`, and reset both `ctx.args` and
   `ctx.protected_args` to empty lists **before** anything is invoked (so the
   multi command's callback sees `ctx.args == []`).
3. **Normal mode** (`self.chain` false), all inside `with ctx:` so the
   context's resources stay open until the result callback has run:
   1. Resolve the subcommand with `self.resolve_command(ctx, args)` →
      `(cmd_name, cmd, rest)`. An unknown name fails here
      (`No such command "x".`) before any callback runs.
   2. Set `ctx.invoked_subcommand = cmd_name`.
   3. Run the multi command's own callback (`Command.invoke(self, ctx)`); its
      return value is ignored. It may set e.g. `ctx.obj`.
   4. Only now create the subcommand context:
      `cmd.make_context(cmd_name, rest, parent=ctx)` (so it inherits `obj`
      and other state set by the callback; `--help` / parse errors for the
      subcommand surface from here).
   5. Within the sub-context (`with sub_ctx:`), invoke
      `sub_ctx.command.invoke(sub_ctx)` and return *process(result)*.
4. **Chain mode**, all inside `with ctx:`:
   1. Set `ctx.invoked_subcommand` to `'*'` if there are leftover arguments,
      else `None`.
   2. Run the multi command's own callback (`Command.invoke(self, ctx)`).
   3. Then, while arguments remain: resolve the next subcommand from the
      remaining arguments, create its context with the
      subcommand's `make_context`, as a child of `ctx`, passing the context
      options `allow_extra_args` (true) and `allow_interspersed_args` (false)
      so that it leaves the arguments it does not own unconsumed; the arguments that subcommand did not
      consume (its `sub_ctx.args`) become the remaining arguments, and its
      `args` is reset to `[]`. **All** subcommand contexts are created
      (i.e. parsed) before **any** subcommand is invoked, so a parse error,
      unknown command or `--help` in a later subcommand prevents earlier
      ones from running.
   4. Invoke the subcommands in command-line order, each within its own
      context (`with sub_ctx:`), collecting their return values in a list.
   5. Return *process(list of results)*.

Examples (`cli` a group, subcommands echo their name):
- normal: `cli sync` → group callback runs (sees
  `ctx.invoked_subcommand == 'sync'`), then `sync`; `cli` alone with
  `invoke_without_command=True` → only the group callback, with
  `invoked_subcommand is None`.
- `@click.group() @click.argument('obj')`: `cli obj1` → `Error: Missing
  command.`; `cli obj1 move` → `obj=obj1`, `move`.
- chain: `cli bdist sdist bdist` → `bdist`, `sdist`, `bdist` called in that
  order; group callback sees `ctx.args == []`; with a result callback
  `process(results, **params)` it receives the list of the three return
  values. With `invoke_without_command=True` and no subcommand, the result
  callback receives `[]`.

## 3. Input specification

`ctx`: the `click.Context` created by `self.make_context(...)` for this
multi command: `ctx.params` holds its parsed parameters; `ctx.protected_args`
/ `ctx.args` hold the leftover strings as described in `context.md`.
`self` attributes used: `chain`, `invoke_without_command`, `result_callback`,
`callback`.

## 4. Output specification

Returns the value described above (own callback result, subcommand result,
list of chained results, or the result callback's return value). Raises
`click.UsageError` for a missing or unknown command; exceptions from
callbacks, parsing, `--help` (`Exit`) propagate unchanged. `ctx.args` and
`ctx.protected_args` are emptied whenever a subcommand is given;
`ctx.invoked_subcommand` is set as described.

## 5. Edge cases and constraints

- In chain mode the same subcommand may appear several times; each
  occurrence gets its own context and invocation.
- Subcommand contexts are children of `ctx` (`parent=ctx`) so nested usage
  errors show the full command path (e.g. `Usage: cmd foo [OPTIONS] BAR`).
- Context close callbacks of `ctx` run after the result callback.
- Not thread-safe (uses the current-context stack).

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

=== STUB ===
```python
def invoke(self, ctx):
    raise NotImplementedError  # TODO: implement according to the specification
```
