You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `is_incomplete_option(all_args, cmd_param)`

## 1. Component overview

Part of click's shell-completion support. When the user presses TAB, the
completion engine (`get_choices`) must decide whether the word being typed
is a *value for an option* (e.g. after `--color`, offer `red`, `green`, ...).
`is_incomplete_option` answers this question for one parameter: does the
tail of the already-typed words show that `cmd_param` is an option that is
still waiting for one of its values?

## 2. Functional requirements

1. Return `False` if `cmd_param` is not a `click.Option` (e.g. a
   `click.Argument`).
2. Return `False` if the option is a flag (`cmd_param.is_flag` true; this
   includes boolean `--x/--no-x` switches and `is_flag=True` options), since
   flags take no value.
3. Ignore every word of `all_args` that is exactly `'='` (bash may split
   `--opt=value` into `--opt`, `=`, `value`).
4. Consider only the *window* of the last `cmd_param.nargs` remaining words
   (fewer if there are not that many). Within that window, find the word
   furthest from the end that starts with `-`. The result is `True` iff such
   a word exists and it is one of the option's primary spellings
   (`cmd_param.opts`); otherwise `False`. Secondary spellings
   (`cmd_param.secondary_opts`) never count.
5. The arguments are not modified.

Examples (option `--opt1` with `nargs=1` unless stated):

| `all_args` | result |
|------------|--------|
| `['--opt1']` | `True` |
| `['--opt1', '=']` | `True` (`'='` is ignored) |
| `['--opt1', 'opt11']` | `False` (value already given) |
| `['--opt1', 'opt11', '--opt1']` | `True` |
| `['--opt2']` | `False` (different option) |
| `[]` | `False` |
| `['-m']` for option `('--message', '-m')` | `True` |

With `--pos` and `nargs=2`:

| `all_args` | result |
|------------|--------|
| `['--pos']` | `True` |
| `['--pos', 'pos1']` | `True` (one value still missing) |
| `['--pos', 'pos1', 'pos2']` | `False` |
| `['x', '--pos']` | `True` |
| `['--pos', '--other']` | `True` (the earlier option in the window wins) |

For a flag `--shout/--no-shout`, `['--shout']` gives `False`.

In `get_choices` this makes, for example, `choices(['--opt1'], '')` offer
the choices of `--opt1`, while `choices(['--opt1', 'opt11'], '')` moves on
to argument or sub-command completion.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `all_args` | `list` of `str` | All words typed so far after the program name (may include `'='` words and words of parent commands). |
| `cmd_param` | `click.Parameter` | A parameter of the innermost command (`Option` or `Argument`). Relevant attributes: `is_flag`, `nargs` (a positive `int` for options), `opts` (list of option strings). |

## 4. Output specification

A `bool`: `True` if `cmd_param` is a value-taking option whose primary
spelling appears in the window described above, else `False`.

## 5. Edge cases and constraints

- Words are compared exactly (no prefix matching, no `=value` splitting;
  `'--opt1=x'` is not equal to `'--opt1'`).
- A word starting with a single `-` (e.g. `-m`, `-`) counts as an option
  word just like `--long` ones.
- Only the last `nargs` non-`'='` words matter; an option string earlier
  than that is ignored.
- If `nargs` is `0` or there are no words, the result is `False`.
- Pure function, no side effects, thread-safe.

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
get_choices( cli , prog_name , args , incomplete )
get_completion_script( prog_name , complete_var , shell )
get_user_autocompletions( ctx , args , incomplete , cmd_param )
get_visible_commands_starting_with( ctx , starts_with )
is_incomplete_argument( current_params , cmd_param )
resolve_ctx( cli , prog_name , args )
start_of_option( param_str )
```

=== STUB ===
```python
def is_incomplete_option(all_args, cmd_param):
    raise NotImplementedError  # TODO: implement according to the specification
```
