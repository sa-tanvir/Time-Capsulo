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
