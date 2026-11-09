# Functional specification: `Help::write_templated_help(&mut self, parser: &Parser, template: &str) -> ClapResult<()>`

## 1. Component overview

Part of `clap` 2.30's help writer (`src/app/help.rs`). An application may replace the
default help layout with a **template** (`App::template`), a text containing tags in
curly braces, e.g.

```
{bin} {version}
{author}
{about}

USAGE:
    {usage}

{all-args}
```

This method writes the template to `self.writer`, copying ordinary text verbatim and
replacing every recognised tag by the corresponding piece of help. The template tests
compare complete help screens, and malformed or unknown tags must be reproduced exactly
as specified below.

## 2. Functional requirements

### 2.1 Scanning

Process the template's **bytes** from left to right:

1. Copy bytes to the output until a `{` is found (the `{` itself is not copied yet).
   If the template ends first, stop.
2. After a `{`, look at **at most the next 15 bytes** for a closing `}`:
   - `}` found at offset `k` (`0 <= k <= 14`): the `k` bytes between the braces are the
     **tag**; both braces and the tag are consumed. Then:
     - `k == 0` (an empty `{}`): write nothing and continue scanning.
     - otherwise handle the tag (2.2) and continue scanning after the `}`.
   - No `}` within those bytes, but at least one byte was read: write `{` followed by
     the bytes that were read (up to 15, verbatim — a `{` among them does **not** start
     a new tag), then continue scanning normally after them.
   - The template ends immediately after the `{`: write nothing more and stop (a
     trailing `{` is dropped).
3. Text outside tags, including a lone `}`, is copied unchanged.

### 2.2 Tags (exact, case-sensitive, no whitespace)

| tag | output |
|---|---|
| `bin` | the binary name, via `self.write_bin_name(parser)` |
| `version` | `parser.meta.version`, or `unknown version` |
| `author` | `parser.meta.author`, or `unknown author` |
| `about` | `parser.meta.about`, or `unknown about` |
| `long-about` | `parser.meta.long_about`, or `unknown about` |
| `usage` | `usage::create_usage_no_title(parser, &[])` |
| `all-args` | `self.write_all_args(parser)` (all sections with headers) |
| `unified` | `self.write_args` over all flags followed by all options |
| `flags` | `self.write_args` over the flags |
| `options` | `self.write_args` over the options |
| `positionals` | `self.write_args` over the positionals |
| `subcommands` | `self.write_subcommands(parser)` |
| `after-help` | `parser.meta.more_help`, or `unknown after-help` |
| `before-help` | `parser.meta.pre_help`, or `unknown before-help` |
| `?` | the text `Could not decode tag name` |
| anything else | written back unchanged: `{`, the tag bytes, `}` |

### 2.3 Result

Return `Ok(())` when the template is exhausted. Any I/O error (or an error returned by a
section writer) is returned immediately, converted to the crate's `Error`.

### Examples (app `MyApp`, version `1.0`, no author/about)

| template | output |
|---|---|
| `""` | `""` |
| `test no tag test` | `test no tag test` |
| `test {unknown_tag} test` | `test {unknown_tag} test` |
| `a{bin}b{version}` | `aMyAppb1.0` |
| `{author}/{about}/{after-help}` | `unknown author/unknown about/unknown after-help` |
| `{?}` | `Could not decode tag name` |
| `{}` | `""` |
| `x{` | `x` |
| `{bin` | `{bin` |
| `}{bin}{` | `}MyApp` |
| `{{bin}}` | `{{bin}}` (tag is `{bin`, unknown) |
| `{ bin }` | `{ bin }` |
| `{BIN}` | `{BIN}` |
| `{this-tag-is-way-too-long} after` | unchanged (no `}` within 15 bytes) |
| `{nope lorem ipsum {bin}` | `{nope lorem ipsu` + `m ` + `MyApp`, i.e. `{nope lorem ipsum MyApp` |

## 3. Input specification

- `self`: the help writer (see "Instance state"); section tags use its width/colour
  settings through the sibling writers.
- `parser`: a fully built `Parser` (meta data and arguments).
- `template`: arbitrary UTF-8 text, possibly empty or very long; braces need not be
  balanced.

## 4. Output specification

- Writes the expanded template to `self.writer`; returns `ClapResult<()>`.
- Ordinary text is reproduced byte-for-byte (including multi-byte characters; the
  15-byte window counts bytes).

## 5. Edge cases and constraints

- The longest tag that can be recognised is 14 bytes; all valid tag names are shorter.
- Repeated tags are expanded each time.
- Must not modify `parser`; must work in a single left-to-right pass (cost linear in the
  template length plus the cost of the expanded sections).
