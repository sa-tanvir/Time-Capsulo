You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `get_choices(cli, prog_name, args, incomplete)`

## 1. Component overview

`get_choices` is the core of click's shell (bash/zsh) completion. Given a
command tree, the words already typed after the program name and the word
currently being typed, it returns the list of candidate completions, each a
`(value, help)` pair. The shell front-end (`do_complete`) prints the values
(and, for zsh, the help strings).

It relies on helpers of the same module (signatures in `context.md`), whose
contracts are:

- `resolve_ctx(cli, prog_name, args)`: parses `args` with resilient parsing
  (errors are tolerated), descends into sub-commands (including chained
  ones) and returns the innermost `click.Context` reached. Parsing consumes
  the list passed in, so `args` may be modified by this call.
- `start_of_option(s)`: truthy iff `s` is non-empty and starts with `-`.
- `is_incomplete_option(all_args, param)`: `True` iff `param` is a non-flag
  `Option` whose option string is among the last words of `all_args` such
  that it is still waiting for (some of) its `nargs` values.
- `is_incomplete_argument(params, param)`: `True` iff `param` is an
  `Argument` that can still accept values given the already parsed values
  `params` (a context's `params` dict).
- `get_user_autocompletions(ctx, args, incomplete, param)`: list of
  `(value, help)` pairs for a parameter: the `Choice` values whose `str`
  starts with `incomplete` (help `None`, in declaration order), or the
  results of the parameter's `autocompletion` callback, or `[]`.
- `add_subcommand_completions(ctx, incomplete, out)`: appends
  `(name, short_help)` pairs to the list `out` for the visible sub-commands
  of `ctx.command` that start with `incomplete`, plus the not-yet-used
  commands of chained parent groups.

## 2. Functional requirements

1. Keep a separate copy of the typed words (`all_args`) that is not affected
   by parsing, then obtain the innermost context via `resolve_ctx`. If it
   returns `None`, return `[]`.
2. Handle `=` as produced by bash word splitting:
   - if `incomplete` starts with `-` and contains `=`, split it at the first
     `=`: the part before is appended to `all_args` (as if the option had
     been typed as its own word) and the part after becomes the new
     `incomplete` (`'--opt1='` completes the values of `--opt1`);
   - otherwise, if `incomplete` is exactly `'='`, treat it as `''`.
   This step happens **after** `resolve_ctx` has been called (and only when it
   returned a context): the part appended to `all_args` is never seen by
   `resolve_ctx`, and the caller's `args` list is not extended with it; only
   the private `all_args` copy (used in steps 3 and 4) gets it.
3. **Option names.** If (the possibly updated) `incomplete` starts with `-`,
   return the option strings of the innermost command: for each parameter of
   `ctx.command.params`, in order, that is an `Option` and not hidden, take
   its `opts` followed by its `secondary_opts`, skip strings already present
   in `all_args` unless the option is `multiple`, keep those starting with
   `incomplete`, and produce `(option_string, option.help)` for each. This
   list is returned unsorted.
4. **Option values.** Otherwise, the first parameter (in
   `ctx.command.params` order) for which `is_incomplete_option(all_args,
   param)` holds determines the result:
   `get_user_autocompletions(ctx, all_args, incomplete, param)`, returned
   as-is.
5. **Argument values.** Otherwise, the first parameter for which
   `is_incomplete_argument(ctx.params, param)` holds determines the result,
   computed the same way.
6. **Sub-commands.** Otherwise collect sub-command completions with
   `add_subcommand_completions(ctx, incomplete, ...)` and return them sorted
   (ascending, comparing the pairs).

Examples (values only unless noted):

- Command with `--opt1` (`Choice(['opt11','opt12'])`, help `'opt1 help'`),
  `--opt2` (`Choice(['opt21','opt22'])`, default `'opt21'`), `--opt3`
  (`Choice(['opt','option'])`):
  `args=[]`, `incomplete='-'` gives
  `[('--opt1','opt1 help'), ('--opt2',None), ('--opt3',None)]`;
  `[]`, `'--opt1='` gives `opt11, opt12`; `['--opt2']`, `'='` gives
  `opt21, opt22`; `['--opt2','=']`, `'opt'` gives `opt21, opt22`;
  `['--opt2','opt21']`, `'-'` gives `--opt1, --opt3`;
  `['--opt3']`, `'opti'` gives `option`.
- `--shout/--no-shout` flag: `'-'` gives `--shout, --no-shout`.
- `--message/-m` with `multiple=True`: `'-'` gives `--message, -m`, and
  they are still offered after being typed.
- Group with commands `bsub` (short help `'bsub help'`) and `csub`, after a
  satisfied argument: `('bsub','bsub help'), ('csub','')`.
- Group `cli` with only an option `--global-opt` and sub-command `sub`:
  `[]`, `''` gives `sub`; `['sub']`, `''` gives `[]`.
- Hidden options and commands are not offered, but typing a hidden option
  or command explicitly still completes its values / sub-commands.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `cli` | `click.BaseCommand` | Root command or group. |
| `prog_name` | `str` | Program name used as the root context's info name. |
| `args` | `list` of `str` | Words already typed after the program name (may be modified by parsing). |
| `incomplete` | `str` | The word being completed (possibly `''`). |

## 4. Output specification

A `list` of 2-tuples `(value, help)`. `value` is an option string,
sub-command name, `Choice` value (any type, e.g. ints) or whatever an
`autocompletion` callback produced; `help` is a string or `None`.
Option-name and parameter-value lists keep their natural order; only the
sub-command case is sorted.

## 5. Edge cases and constraints

- Invalid or unknown words never raise; parsing is resilient.
- A non-group command with nothing left to complete gives `[]`.
- An option whose `nargs` values are all present no longer counts as
  incomplete (`--pos` with `nargs=2`: `['--pos','1.0','1.0']` falls through
  to sub-commands).
- Nothing is printed and no command callback is invoked; the only side
  effect is that `args` may be consumed by parsing.

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `click/_bashcomplete.py`

## Imports / includes available in this file

```
import copy
import os
import re
from .utils import echo
from .parser import split_arg_string
from .core import MultiCommand, Option, Argument
from .types import Choice
```

## Other functions defined in the same file (signatures only; you may call them)

```
add_subcommand_completions( ctx , incomplete , completions_out )
bashcomplete( cli , prog_name , complete_var , complete_instr )
do_complete( cli , prog_name , include_descriptions )
get_completion_script( prog_name , complete_var , shell )
get_user_autocompletions( ctx , args , incomplete , cmd_param )
get_visible_commands_starting_with( ctx , starts_with )
is_incomplete_argument( current_params , cmd_param )
is_incomplete_option( all_args , cmd_param )
resolve_ctx( cli , prog_name , args )
start_of_option( param_str )
```

=== STUB ===
```python
def get_choices(cli, prog_name, args, incomplete):
    raise NotImplementedError  # TODO: implement according to the specification
```
