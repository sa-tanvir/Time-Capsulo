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
