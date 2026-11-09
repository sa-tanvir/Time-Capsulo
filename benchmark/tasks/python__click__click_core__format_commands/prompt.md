You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `MultiCommand.format_commands(self, ctx, formatter)`

## 1. Component overview

`MultiCommand.format_commands` writes the `Commands:` section of a group's
`--help` page: one row per visible subcommand, with the subcommand name on the
left and its short help on the right. It is called by the help machinery after
the options section has been written. The members it relies on
(`list_commands`, `get_command`, `Command.hidden`,
`Command.get_short_help_str`, `HelpFormatter.width`, `HelpFormatter.section`,
`HelpFormatter.write_dl`) are described in `context.md`.

## 2. Functional requirements

1. **Collect the visible subcommands.** Ask `self.list_commands(ctx)` for the
   subcommand names and, for each name in the order returned, look the command
   up with `self.get_command(ctx, name)`.
   - If the lookup returns `None` (a name was listed that does not exist),
     silently ignore that name.
   - If the command is hidden (`cmd.hidden` truthy), ignore it. A hidden
     subgroup is ignored as a whole; its own subcommands are never listed here.
   - Otherwise keep the pair (listed name, command). Duplicate names are kept
     as many times as they are listed.
2. **Nothing to show.** If no subcommand was kept, write nothing at all to the
   formatter (no heading, no blank line).
3. **Short-help width.** Compute `limit = formatter.width - 6 - L`, where `L`
   is the length (in characters) of the longest *listed name* among the kept
   subcommands. (The listed name is used, not `cmd.name`.)
4. **Rows.** For each kept subcommand, in order, build the row
   `(listed_name, cmd.get_short_help_str(limit))`. The short help is therefore
   the command's explicit `short_help` if it has one, otherwise its help text
   condensed to `limit` characters, or `''`.
5. **Output.** Inside `formatter.section('Commands')`, write all rows with a
   single `formatter.write_dl(rows)` call (default column arguments).
6. Return `None`.

Example: a group with subcommands registered as `short` (help
`"This is a short text."`), `special-chars` (help
`"Login and store the token in ~/.netrc."`) and `long` (help
`"This is a long text that is too long to show as short help\n and will be truncated instead."`),
formatted with an 80-column formatter, yields (names sorted by the group):

```
Commands:
  long           This is a long text that is too long to show as short help...
  short          This is a short text.
  special-chars  Login and store the token in ~/.netrc.
```

Here `L = 13` (`special-chars`), so `limit = 80 - 6 - 13 = 61`.

A group whose only subcommand is `hidden=True` (or a hidden subgroup) produces
no `Commands:` section, and neither the hidden name nor the names of the
hidden subgroup's children appear in the help output.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `click.MultiCommand` (e.g. `click.Group`) | The command whose subcommands are listed. |
| `ctx` | `click.Context` | Current context; only passed through to `list_commands` / `get_command`. |
| `formatter` | `click.HelpFormatter` | Output sink; its `width` (int, columns) is read. |

## 4. Output specification

Returns `None`. The effect is the text written into `formatter`: either nothing,
or exactly one `Commands` section containing one definition-list row per visible
subcommand, in `list_commands` order. `self`, `ctx` and the subcommands are not
modified.

## 5. Edge cases and constraints

- Empty `list_commands` result, all names unknown, or all commands hidden: no
  output.
- `limit` may become small or negative for very long names or narrow
  formatters; it is passed to `get_short_help_str` unchanged.
- Commands with an explicit `short_help` show it verbatim regardless of
  `limit`; commands without any help get an empty description.
- Works for chained groups and groups with arguments exactly the same way.
- No I/O other than writing to the given formatter.

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

=== STUB ===
```python
def format_commands(self, ctx, formatter):
    raise NotImplementedError  # TODO: implement according to the specification
```
