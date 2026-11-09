You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `add_subcommand_completions(ctx, incomplete, completions_out)`

## 1. Component overview

Part of click's shell (bash/zsh) completion. After the completion engine
(`get_choices`) has parsed the typed words into a chain of `click.Context`
objects and decided that the current word is neither an option name nor a
parameter value, it asks this function for the *sub-command names* that may
be typed next. Candidates come from the innermost command itself (if it is a
group) and from any **chained** groups further up the context chain, since a
chained group (`@click.group(chain=True)`) accepts several sub-commands in a
row.

A helper of the same module is available (signature in `context.md`):
`get_visible_commands_starting_with(ctx, starts_with)` yields the command
objects of the multi-command `ctx.command` whose listed names (in the order
of `ctx.command.list_commands(ctx)`, i.e. sorted for `click.Group`) start
with `starts_with`, skipping commands marked `hidden`.

## 2. Functional requirements

1. The function appends `(name, help)` pairs to the list `completions_out`
   (mutating it in place) and returns `None`. Existing items of the list are
   kept. `name` is the command object's `name` attribute and `help` is the
   result of its `get_short_help_str()` method (the explicit `short_help`,
   or a shortened form of `help`, or `''`).
2. **Own sub-commands.** If `ctx.command` is a `click.MultiCommand` (e.g. a
   `click.Group`, chained or not), first append a pair for every visible
   sub-command of `ctx.command` whose name starts with `incomplete`, in
   listing order.
3. **Chained ancestors.** Then walk up the context chain through
   `ctx.parent`, from the nearest parent to the root. For every ancestor
   context whose command is a `MultiCommand` with `chain` true, append a
   pair for every visible sub-command of that ancestor whose name starts
   with `incomplete` **and** whose name does not occur in that ancestor
   context's `protected_args` (the chained sub-command words already typed
   at that level), in listing order. Ancestors that are not chained groups
   contribute nothing, but the walk continues past them.
4. Nothing is de-duplicated or sorted (the caller sorts).

Examples (results shown after sorting by the caller, as in `get_choices`):

- Chained group `cli` (argument `arg`, commands `asub`, `bsub` with help
  `'bsub help'`, `csub`): with typed words `['cliarg1', 'asub']` and
  `incomplete=''`, the innermost context is `asub` (not a group); its
  parent `cli` is chained and has `protected_args == ['asub']`, so the
  completions are `[('bsub', 'bsub help'), ('csub', '')]`; with
  `incomplete='b'` only `('bsub', 'bsub help')`.
- Group `cli` → group `sub` → chained group `csub` with commands `dsub` and
  `esub`: for typed words `['sub']` the result is `bsub, csub` (the
  sub-commands of `sub`); for `['sub', 'csub']` it is `dsub, esub`; for
  `['sub', 'csub', 'dsub']` it is `esub` only.
- Plain (non-chained) group with sub-command `sub`: typed `[]` gives `sub`;
  typed `['sub']` (innermost is a plain command) gives nothing.
- Hidden sub-commands are never offered, but a hidden group's own children
  are offered once the user has typed the hidden group's name.
- Group `cli` → group `sub` whose sub-commands are `bsub` (declared with
  `short_help='bsub help'`) and group `csub` (no help): with the innermost
  context at `sub` the pairs are `('bsub', 'bsub help'), ('csub', '')`.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `ctx` | `click.Context` | Innermost context produced by resilient parsing; may have a chain of `parent` contexts ending at the root (`parent is None`). |
| `incomplete` | `str` | Prefix the command names must start with (`''` matches all). |
| `completions_out` | `list` | Output list, extended in place. |

## 4. Output specification

Returns `None`. Side effect: `completions_out` is extended with 2-tuples
`(command_name: str, short_help: str)`, first those of `ctx.command` (if it
is a multi-command), then those of each chained ancestor, nearest first.
`ctx` and its parents are not modified.

## 5. Edge cases and constraints

- If `ctx.command` is a plain `Command` and no ancestor is chained, nothing
  is appended.
- If `ctx.command` is itself a chained group, its own sub-commands are
  added by rule 2 without filtering by `protected_args`; the filtering only
  applies to ancestors.
- Matching is a case-sensitive prefix test on the listed name.
- No output is printed; not thread-safe with respect to the shared output
  list.

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
bashcomplete( cli , prog_name , complete_var , complete_instr )
do_complete( cli , prog_name , include_descriptions )
get_choices( cli , prog_name , args , incomplete )
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
def add_subcommand_completions(ctx, incomplete, completions_out):
    raise NotImplementedError  # TODO: implement according to the specification
```
