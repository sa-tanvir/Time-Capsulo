You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `OptionParser._match_long_opt(self, opt, explicit_value, state)`

## 1. Component overview

`click.parser.OptionParser` is click's low-level command-line parser. While it
walks the argument list, every token that looks like an option is first tried
as a *long* option: `--name`, `-name`, `+name`, `/name`, … — i.e. any option
string that is not a single prefix character followed by a single character.
`_match_long_opt` handles one such token: it looks the (already normalised)
option string up among the parser's registered long option strings, collects
the option's value(s) from the remaining arguments, and records the result in
the parsing state. The relevant parser, option and state attributes are shown
in `context.md`.

## 2. Functional requirements

1. **Unknown option.** If `opt` is not one of the parser's registered long
   option strings (exact, case-sensitive match), raise
   `click.exceptions.NoSuchOption` with `option_name=opt`, the default
   message (`no such option: <opt>`), `ctx=self.ctx`, and `possibilities`
   set to the list of all registered long option strings that **start with**
   `opt` (in registration order; an empty list when none match). The state
   is not modified. Example: with `--verbose` and `--version` registered,
   `opt='--ver'` raises an error whose `possibilities` are
   `['--verbose', '--version']`; `opt='--foo'` raises with `[]` and the
   message `no such option: --foo`.
2. Otherwise let `option` be the registered option for `opt`.
3. **Option that takes a value** (`option.takes_value` is true, i.e. action
   `store` or `append`):
   - If `explicit_value` is not `None` (the user wrote `--name=value`), it is
     used as the **first** value for the option, ahead of the remaining
     arguments in `state.rargs`.
   - The option consumes exactly `option.nargs` values, taken in order from
     the front (explicit value first, then `state.rargs`). The consumed
     values are removed from `state.rargs`; the other remaining arguments
     stay, in order.
   - If fewer than `nargs` values are available, raise
     `click.exceptions.BadOptionUsage` (option name `opt`) with message
     `<opt> option requires an argument` when `nargs == 1`, or
     `<opt> option requires <nargs> arguments` otherwise (e.g.
     `--foo option requires 2 arguments`). `_error_opt_args(nargs, opt)` raises
     exactly this (with no context: `ctx` is `None`). Nothing is recorded in
     `state.opts`/`state.order`. `state.rargs` is then left as follows: when
     `explicit_value` is `None` it is unchanged; when an explicit value was
     given, it is left with that value inserted at the front (`'--pt'`, `'1'`,
     `[]` raises and leaves `rargs == ['1']`).
   - The value passed on is the single string when `nargs == 1`, or a
     `tuple` of the `nargs` strings when `nargs > 1`.
   - Values are taken verbatim, even if they look like options (`-x`, `--`).
4. **Option that takes no value** (flags, counts, constants):
   - If `explicit_value` is not `None` (even the empty string), raise
     `click.exceptions.BadOptionUsage` (option name `opt`) with message
     `<opt> option does not take a value` (no context attached). Nothing is
     recorded and `state.rargs` is unchanged.
   - Otherwise the value is `None` and no argument is consumed.
5. Finally record the result by calling `option.process(value, state)`
   exactly once, which updates `state.opts` and appends to `state.order`.
6. Returns `None`.

Examples (parser with `--name` (store, nargs 1), `--pt` (store, nargs 2),
`--flag` (store_const)):

| opt, explicit_value, rargs before | effect |
|---|---|
| `'--name'`, `None`, `['a', 'b']` | `opts['name'] = 'a'`, rargs `['b']` |
| `'--name'`, `'x'`, `['a']` | `opts['name'] = 'x'`, rargs `['a']` |
| `'--pt'`, `'1'`, `['2', '3']` | `opts['pt'] = ('1', '2')`, rargs `['3']` |
| `'--pt'`, `None`, `['1']` | `BadOptionUsage`: `--pt option requires 2 arguments` |
| `'--name'`, `None`, `[]` | `BadOptionUsage`: `--name option requires an argument` |
| `'--flag'`, `'1'`, `[]` | `BadOptionUsage`: `--flag option does not take a value` |
| `'--flag'`, `None`, `['a']` | `opts['flag']` set to its constant, rargs `['a']` |

At the command level these surface e.g. as `Error: no such option: --foo`
(click adds `Did you mean …?` when exactly one possibility exists) and
`Error: --foo option requires an argument`.

## 3. Input specification

| Parameter | Type | Meaning |
|---|---|---|
| `self` | `OptionParser` | Parser with registered options; `self.ctx` is a `click.Context` or `None`. |
| `opt` | `str` | The option string, already normalised by the caller. |
| `explicit_value` | `str` or `None` | Value attached with `=`, or `None` when absent. |
| `state` | `ParsingState` | `state.rargs` is a `list` of `str` still to be processed. |

## 4. Output specification

Returns `None`. Effects: `state.rargs` loses the consumed values;
`option.process` updates `state.opts` / `state.order`. Errors are
`NoSuchOption` / `BadOptionUsage` (both `click.UsageError` subclasses) as
described, with `ctx`/`option_name` set as stated.

## 5. Edge cases and constraints

- Lookup is exact: `--Name` does not match `--name`; a short string like
  `-f` is "unknown" here unless it was registered as a long option.
- `explicit_value == ''` counts as a given value (it is consumed as the
  empty string for value options, and is an error for flags).
- `state.largs` is never touched; `state.rargs` is mutated in place.
- Called many times per parse; must not modify the parser's registrations.
  Not thread-safe with respect to a shared `state`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `click/parser.py`
- **Enclosing scope:** `class OptionParser(object)`

## Imports / includes available in this file

```
import re
from collections import deque
from .exceptions import UsageError, NoSuchOption, BadOptionUsage, \
```

## Other functions defined in the same file (signatures only; you may call them)

```
_error_opt_args( nargs , opt )
_match_short_opt( self , arg , state )
_process_args_for_args( self , state )
_process_args_for_options( self , state )
_process_opts( self , arg , state )
_unpack_args( args , nargs_spec )
_unpack_args._fetch( c )
add_argument( self , dest , nargs = 1 , obj = None )
add_option( self , opts , dest , action = None , nargs = 1 , const = None , obj = None )
normalize_opt( opt , ctx )
parse_args( self , args )
process( self , value , state )
split_arg_string( string )
split_opt( opt )
takes_value( self )
```


## Other definitions in `click/parser.py` and `click/exceptions.py` (you may rely on them)

```
def _error_opt_args(nargs, opt):
    if nargs == 1:
        raise BadOptionUsage(opt, '%s option requires an argument' % opt)
    raise BadOptionUsage(opt, '%s option requires %d arguments' % (opt, nargs))


def normalize_opt(opt, ctx):
    if ctx is None or ctx.token_normalize_func is None:
        return opt
    prefix, opt = split_opt(opt)
    return prefix + ctx.token_normalize_func(opt)


class Option(object):
    # one registered parser option
    def __init__(self, opts, dest, action=None, nargs=1, const=None, obj=None):
        ...
        self.dest = dest
        self.action = action      # 'store', 'store_const', 'append', 'append_const' or 'count'
        self.nargs = nargs
        self.const = const
        self.obj = obj

    @property
    def takes_value(self):
        return self.action in ('store', 'append')

    def process(self, value, state):
        """Records `value` (or the option's constant / count) in state.opts
        according to the action and appends self.obj to state.order."""


class ParsingState(object):
    def __init__(self, rargs):
        self.opts = {}       # dest -> value
        self.largs = []      # leftover positional/unprocessed args
        self.rargs = rargs   # remaining args still to be processed (a list)
        self.order = []


class OptionParser(object):
    def __init__(self, ctx=None):
        self.ctx = ctx                      # click.Context or None
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False  # copied from ctx when ctx is given
        ...
        self._short_opt = {}   # registered one-character option string (e.g. '-f') -> Option
        self._long_opt = {}    # every other registered option string (e.g. '--foo', '-foo') -> Option
        self._opt_prefixes = set(['-', '--'])


class NoSuchOption(UsageError):
    def __init__(self, option_name, message=None, possibilities=None, ctx=None):
        # default message: 'no such option: <option_name>'
        ...

class BadOptionUsage(UsageError):
    def __init__(self, option_name, message, ctx=None): ...
```

=== STUB ===
```python
def _match_long_opt(self, opt, explicit_value, state):
    raise NotImplementedError  # TODO: implement according to the specification
```
