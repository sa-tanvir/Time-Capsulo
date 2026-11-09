# Functional specification: `Option.get_help_record(self, ctx)`

## 1. Component overview

`Option.get_help_record` produces the two-column entry that represents one
command-line option in a command's `--help` page: the left column lists the
option's spellings (with its value placeholder), the right column holds the
help text plus optional bracketed annotations (environment variable, default
value, "required"). The help formatter prints these records under
`Options:`. The relevant attributes of the option are listed in `context.md`.

## 2. Functional requirements

1. If the option is hidden (`self.hidden` truthy), return `None`; it does not
   appear in help output.
2. **Left column.** Build one text fragment for the primary spellings
   `self.opts` and, if `self.secondary_opts` is non-empty, a second fragment
   for the secondary spellings. Each fragment is the first element returned by
   `join_options` for that list (shortest prefix first, joined by `", "`).
   Unless the option is a flag (`self.is_flag`) or a counting option
   (`self.count`), each fragment is followed by a single space and the result
   of `self.make_metavar()`.
   The fragments are joined with `"; "` if any spelling in either list has
   the `/` prefix (as reported by `join_options`), otherwise with `" / "`.
3. **Right column.** Start from `self.help`, or the empty string if it is
   `None`/empty. The help text is used verbatim (no re-wrapping or stripping).
   Then collect annotations, in this order:
   - *Environment variable* (only when `self.show_envvar` is truthy): the
     variable is `self.envvar`; if that is `None`, the option allows automatic
     env vars (`self.allow_from_autoenv`) and `ctx.auto_envvar_prefix` is not
     `None`, the variable name is `<prefix>_<NAME>` where `<NAME>` is
     `self.name` upper-cased. If the variable is not `None` (an empty
     string still counts), add `env var: <value>`, where a list/tuple of
     names is rendered as `str()` of each item joined by `", "`, and any
     other value (a string, or e.g. an `int` or another object) is rendered
     with `str()` (`envvar=5` gives `env var: 5`).
   - *Default* (only when `self.default is not None` and `self.show_default`
     is truthy): add `default: <text>` where `<text>` is
     - `(<show_default>)` if `show_default` is a string (it replaces the
       value, e.g. `show_default='current user'` gives
       `default: (current user)`);
     - otherwise, for a list/tuple default, its items converted with `str`
       and joined by `", "` (`('foo', 'bar')` gives `default: foo, bar`;
       `(1, 2)` gives `default: 1, 2`);
     - otherwise, if the default is a Python function (as determined by
       `inspect.isfunction`, e.g. a lambda), the literal `(dynamic)`;
     - otherwise the default formatted with `format(default)` (i.e. as
       `'{}'.format(default)`; equal to `str(default)` for ordinary values,
       e.g. `default: 42`, `default: False`).
   - *Required*: if `self.required` is truthy, add `required`.
   If there is at least one annotation, the right column becomes the help
   text, followed by two spaces when the help text is non-empty, followed by
   `[` + the annotations joined by `"; "` + `]`.
4. Return the tuple `(left, right)`.

Examples (help output lines shown as produced by the formatter):

- `@click.option('--method', type=click.Choice(['foo','bar','baz']))`
  gives `('--method [foo|bar|baz]', '')`.
- `@click.option('-v', count=True, help='Verbosity')` gives
  `('-v', 'Verbosity')` (no metavar for counting options).
- `@click.option('++foo', is_flag=True, help='das foo')` gives
  `('++foo', 'das foo')`.
- `@click.option('/debug;/no-debug', help='Enables or disables debug mode.')`
  gives `('/debug; /no-debug', 'Enables or disables debug mode.')`;
  `'--shout/--no-shout'` gives `'--shout / --no-shout'`.
- `@click.option('-n', '--name', help='Name.', required=True)` gives
  `('-n, --name TEXT', 'Name.  [required]')`.
- `@click.option('--arg1', show_envvar=True)` in a context with
  `auto_envvar_prefix='TEST'` gives `('--arg1 TEXT', '[env var: TEST_ARG1]')`.
- `envvar='ARG1', show_envvar=True, default=3, show_default=True,
  help='x'` gives right column `'x  [env var: ARG1; default: 3]'`.
- `default=lambda: ..., show_default=True` gives `'[default: (dynamic)]'`.

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `click.Option` | Fully constructed option (see `context.md`). |
| `ctx` | `click.Context` | Current context; only `ctx.auto_envvar_prefix` (string or `None`) is consulted. |

## 4. Output specification

`None` for hidden options, otherwise a 2-tuple of native strings
`(option_spellings, help_text)`. The option object and the context are not
modified.

## 5. Edge cases and constraints

- A `default` of `None` never produces a default annotation, even with
  `show_default=True`; `show_default` set to a string still requires a
  non-`None` default.
- An option with no help text and no annotations has `''` as right column.
- A falsy-but-not-`None` default (e.g. `0`, `False`, `''`) is shown when
  `show_default` is truthy.
- An explicit `self.envvar` takes precedence over the automatic name.
- Multi-line help text is returned unchanged.
- Pure function of its inputs; no I/O.
