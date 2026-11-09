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
