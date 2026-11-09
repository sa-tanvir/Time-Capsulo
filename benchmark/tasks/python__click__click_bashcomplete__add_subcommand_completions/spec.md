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
