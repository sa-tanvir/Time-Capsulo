You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `Option.get_help_record(self, ctx)`

## 1. Component overview

`Option.get_help_record` produces the two-column entry that represents one
command-line option in a command's `--help` page: the left column lists the
option's spellings (with its value placeholder), the right column holds the
help text plus optional bracketed annotations (environment variable, default
value, "required"). The help formatter prints these records under
`Options:`. The relevant attributes of the option are listed in `context.md`.

## 2. Functional requirements

1. If the option is hidden (`self.hidden` truthy), return `None`; it does not
   appear in help output.
2. **Left column.** Build one text fragment for the primary spellings
   `self.opts` and, if `self.secondary_opts` is non-empty, a second fragment
   for the secondary spellings. Each fragment is the first element returned by
   `join_options` for that list (shortest prefix first, joined by `", "`).
   Unless the option is a flag (`self.is_flag`) or a counting option
   (`self.count`), each fragment is followed by a single space and the result
   of `self.make_metavar()`.
   The fragments are joined with `"; "` if any spelling in either list has
   the `/` prefix (as reported by `join_options`), otherwise with `" / "`.
3. **Right column.** Start from `self.help`, or the empty string if it is
   `None`/empty. The help text is used verbatim (no re-wrapping or stripping).
   Then collect annotations, in this order:
   - *Environment variable* (only when `self.show_envvar` is truthy): the
     variable is `self.envvar`; if that is `None`, the option allows automatic
     env vars (`self.allow_from_autoenv`) and `ctx.auto_envvar_prefix` is not
     `None`, the variable name is `<prefix>_<NAME>` where `<NAME>` is
     `self.name` upper-cased. If the variable is not `None` (an empty
     string still counts), add `env var: <value>`, where a list/tuple of
     names is rendered as `str()` of each item joined by `", "`, and any
     other value (a string, or e.g. an `int` or another object) is rendered
     with `str()` (`envvar=5` gives `env var: 5`).
   - *Default* (only when `self.default is not None` and `self.show_default`
     is truthy): add `default: <text>` where `<text>` is
     - `(<show_default>)` if `show_default` is a string (it replaces the
       value, e.g. `show_default='current user'` gives
       `default: (current user)`);
     - otherwise, for a list/tuple default, its items converted with `str`
       and joined by `", "` (`('foo', 'bar')` gives `default: foo, bar`;
       `(1, 2)` gives `default: 1, 2`);
     - otherwise, if the default is a Python function (as determined by
       `inspect.isfunction`, e.g. a lambda), the literal `(dynamic)`;
     - otherwise the default formatted with `format(default)` (i.e. as
       `'{}'.format(default)`; equal to `str(default)` for ordinary values,
       e.g. `default: 42`, `default: False`).
   - *Required*: if `self.required` is truthy, add `required`.
   If there is at least one annotation, the right column becomes the help
   text, followed by two spaces when the help text is non-empty, followed by
   `[` + the annotations joined by `"; "` + `]`.
4. Return the tuple `(left, right)`.

Examples (help output lines shown as produced by the formatter):

- `@click.option('--method', type=click.Choice(['foo','bar','baz']))`
  gives `('--method [foo|bar|baz]', '')`.
- `@click.option('-v', count=True, help='Verbosity')` gives
  `('-v', 'Verbosity')` (no metavar for counting options).
- `@click.option('++foo', is_flag=True, help='das foo')` gives
  `('++foo', 'das foo')`.
- `@click.option('/debug;/no-debug', help='Enables or disables debug mode.')`
  gives `('/debug; /no-debug', 'Enables or disables debug mode.')`;
  `'--shout/--no-shout'` gives `'--shout / --no-shout'`.
- `@click.option('-n', '--name', help='Name.', required=True)` gives
  `('-n, --name TEXT', 'Name.  [required]')`.
- `@click.option('--arg1', show_envvar=True)` in a context with
  `auto_envvar_prefix='TEST'` gives `('--arg1 TEXT', '[env var: TEST_ARG1]')`.
- `envvar='ARG1', show_envvar=True, default=3, show_default=True,
  help='x'` gives right column `'x  [env var: ARG1; default: 3]'`.
- `default=lambda: ..., show_default=True` gives `'[default: (dynamic)]'`.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `click.Option` | Fully constructed option (see `context.md`). |
| `ctx` | `click.Context` | Current context; only `ctx.auto_envvar_prefix` (string or `None`) is consulted. |

## 4. Output specification

`None` for hidden options, otherwise a 2-tuple of native strings
`(option_spellings, help_text)`. The option object and the context are not
modified.

## 5. Edge cases and constraints

- A `default` of `None` never produces a default annotation, even with
  `show_default=True`; `show_default` set to a string still requires a
  non-`None` default.
- An option with no help text and no annotations has `''` as right column.
- A falsy-but-not-`None` default (e.g. `0`, `False`, `''`) is shown when
  `show_default` is truthy.
- An explicit `self.envvar` takes precedence over the automatic name.
- Multi-line help text is returned unchanged.
- Pure function of its inputs; no I/O.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `click/core.py`
- **Enclosing scope:** `class Option(Parameter)`

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


## Other members of the enclosing class `Option` and its base `Parameter` (you may rely on them)

```
class Parameter(object):
    def __init__(self, param_decls=None, type=None, required=False,
                 default=None, callback=None, nargs=None, metavar=None,
                 expose_value=True, is_eager=False, envvar=None,
                 autocompletion=None):
        self.name, self.opts, self.secondary_opts = \
            self._parse_decls(param_decls or (), expose_value)
        self.type = convert_type(type, default)
        ...
        self.required = required
        self.nargs = nargs
        self.default = default
        self.metavar = metavar
        self.envvar = envvar
        ...

    def make_metavar(self):
        if self.metavar is not None:
            return self.metavar
        metavar = self.type.get_metavar(self)
        if metavar is None:
            metavar = self.type.name.upper()
        if self.nargs != 1:
            metavar += '...'
        return metavar


class Option(Parameter):
    def __init__(self, param_decls=None, show_default=False,
                 prompt=False, confirmation_prompt=False,
                 hide_input=False, is_flag=None, flag_value=None,
                 multiple=False, count=False, allow_from_autoenv=True,
                 type=None, help=None, hidden=False, show_choices=True,
                 show_envvar=False, **attrs):
        # (abridged: only the attributes relevant here)
        self.hidden = hidden
        self.is_flag = is_flag          # resolved to a bool
        self.count = count
        self.multiple = multiple
        self.allow_from_autoenv = allow_from_autoenv
        self.help = help
        self.show_default = show_default
        self.show_choices = show_choices
        self.show_envvar = show_envvar

    # def get_help_record(self, ctx):  <- the method to implement
```

`join_options(options)` (imported from `.formatting`): given a list of option
strings, returns `(formatted_string, any_prefix_is_slash)`; the strings are
ordered by prefix length (shortest prefix first, stable) and joined with
`', '`, and the flag is `True` when any option's prefix is `/`.
For example `join_options(['--verbose', '-v'])` is `('-v, --verbose', False)`.

=== STUB ===
```python
def get_help_record(self, ctx):
    raise NotImplementedError  # TODO: implement according to the specification
```
