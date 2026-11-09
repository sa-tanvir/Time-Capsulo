You are an expert Rust developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Rust code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```rust code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** rust
- **File:** `src/completions/fish.rs`

## Imports / includes available in this file

```
use std::io::Write;
use app::parser::Parser;
```

## Other functions defined in the same file (signatures only; you may call them)

```
escape_string string : & str
generate_to & self , buf : & mut W
new p : & b Parser < a , b >
```

## Data used by this function

- `comp_gen: &FishGen` — `comp_gen.p: &Parser`, the (sub)command whose completions are generated;
  `FishGen::new(p: &Parser) -> FishGen` wraps another parser.
- `Parser`: `p.opts()` / `p.flags()` — iterators over `&OptBuilder` / `&FlagBuilder` in declaration order;
  `p.subcommands: Vec<App>` in declaration order; each `App` has `.p: Parser` whose `p.meta.name: String` is the
  subcommand name and `p.meta.about: Option<&str>` its description.
- `OptBuilder` / `FlagBuilder` public fields: `.s.short: Option<char>`, `.s.long: Option<&str>` (no dashes),
  `.b.help: Option<&str>`; options also `.v.possible_vals: Option<Vec<&str>>`.
- `escape_string(string: &str) -> String` (same file): escapes text for use inside fish single quotes
  (`\` → `\\`, `'` → `\'`).

=== STUB ===
```rust
fn gen_fish_inner(root_command: &str, comp_gen: &FishGen, parent_cmds: &str, buffer: &mut String) {
    // TODO: implement according to the specification
}
```
