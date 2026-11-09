# Functional specification: `gen_fish_inner(root_command: &str, comp_gen: &FishGen, parent_cmds: &str, buffer: &mut String)`

## 1. Component overview

Part of `clap` 2.30's shell-completion generator for the **fish** shell
(`src/completions/fish.rs`). `FishGen::generate_to` writes a small helper function
followed by the output of `gen_fish_inner`, which appends one fish `complete` command per
option, flag and subcommand of a command, and then recurses into every subcommand. The
completion test compares the full generated script, e.g.

```
complete -c myapp -n "__fish_using_command myapp" -s h -l help -d 'Prints help information'
complete -c myapp -n "__fish_using_command myapp" -s V -l version -d 'Prints version information'
complete -c myapp -n "__fish_using_command myapp" -f -a "test" -d 'tests things'
complete -c myapp -n "__fish_using_command myapp test" -l case -d 'the case to test'
```

## 2. Functional requirements

Let `P = comp_gen.p` and let the **prefix** be

`complete -c <root_command> -n "__fish_using_command <parent_cmds>"`

(exact spacing; `<…>` replaced verbatim, no escaping). Append to `buffer`, each line
terminated by `"\n"`, in this order:

1. **Options** — for every option of `P` (declaration order): the prefix, then
   - ` -s <short>` if it has a short switch,
   - ` -l <long>` if it has a long switch,
   - ` -d '<escaped help>'` if it has help text (`escape_string` applied),
   - ` -r -f -a "<v1> <v2> …"` if it has possible values (joined by single spaces, not
     escaped).
2. **Flags** — for every flag of `P`: the prefix, then ` -s <short>`, ` -l <long>`,
   ` -d '<escaped help>'` under the same conditions (flags have no possible values).
3. **Subcommand names** — for every subcommand of `P` (declaration order): the prefix,
   then ` -f -a "<name>"`, then ` -d '<escaped about>'` if the subcommand has an `about`
   text.
4. **Recursion** — then, for every subcommand (same order), call `gen_fish_inner`
   with the same `root_command`, a `FishGen` for the subcommand's parser, and
   `parent_cmds` extended by the subcommand name: `parent_cmds + " " + name`, or just
   `name` if `parent_cmds` is empty.

All options, flags and subcommands are included (hidden ones too; positional arguments
are never listed). Nothing is cleared or written before the appended text; existing
content of `buffer` is kept.

Example: root `myapp`, parent `myapp`, option `--config`/`-c` with help
`it's a "file"` and possible values `a`, `b`; flag `-v` without help; subcommand `test`
(about `tests things`) that has a flag `--case` with help `the case`:

```
complete -c myapp -n "__fish_using_command myapp" -s c -l config -d 'it\'s a "file"' -r -f -a "a b"
complete -c myapp -n "__fish_using_command myapp" -s v
complete -c myapp -n "__fish_using_command myapp" -f -a "test" -d 'tests things'
complete -c myapp -n "__fish_using_command myapp test" -l case -d 'the case'
```

## 3. Input specification

- `root_command`: the binary name used after `-c`.
- `comp_gen`: generator wrapping the parser of the current (sub)command.
- `parent_cmds`: space-separated command path for the `-n` condition (may be empty).
- `buffer`: output string, appended to.
- Help/about texts may contain quotes, backslashes and any Unicode.

## 4. Output specification

- Returns nothing; all output is appended to `buffer` as described, depth-first
  (all lines of a command before the lines of its subcommands, subcommands in
  declaration order).

## 5. Edge cases and constraints

- A command with no options, flags or subcommands appends nothing.
- With an empty `parent_cmds` the condition is `"__fish_using_command "` (trailing
  space) and the first subcommand level gets just `<name>` as its path.
- Short switches are written as the bare character, long switches without dashes.
- Only help/about text is escaped; names and possible values are inserted unchanged.
- Cost should be linear in the total size of the generated text.
