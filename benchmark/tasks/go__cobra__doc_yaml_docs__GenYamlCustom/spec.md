# Functional specification: `func GenYamlCustom(cmd *cobra.Command, w io.Writer, linkHandler func(string) string) error`

## 1. Component overview

Package `doc` (`github.com/spf13/cobra/doc`) generates reference
documentation for cobra command trees. `GenYamlCustom` writes the
documentation of a single command as one YAML document to `w`.
`GenYaml(cmd, w)` calls it with an identity `linkHandler`, and
`GenYamlTreeCustom` calls it once per file. The document is the YAML
serialisation (`gopkg.in/yaml.v2`, `yaml.Marshal`) of a `cmdDoc` value (see the
context for the type and its YAML field names/`omitempty` rules).

## 2. Functional requirements

1. **Initialisation (side effects on `cmd`).** First call
   `cmd.InitDefaultHelpCmd()` and `cmd.InitDefaultHelpFlag()`, so the
   automatic `help` sub-command (when `cmd` has sub-commands) and the
   `--help/-h` flag exist; the `help` flag therefore appears among the options.
2. Fill a `cmdDoc`:
   - `Name`: `cmd.CommandPath()` (e.g. `root echo`).
   - `Synopsis`: `forceMultiLine(cmd.Short)`.
   - `Description`: `forceMultiLine(cmd.Long)`.
   - `Example`: `cmd.Example` (verbatim; left empty when there is none).
   - `Options`: if `cmd.NonInheritedFlags()` contains any flag (`HasFlags()`,
     hidden flags count), `genFlagResult` of that set; otherwise left empty.
   - `InheritedOptions`: likewise for `cmd.InheritedFlags()`.
   - `SeeAlso`: only if `hasSeeAlso(cmd)` is true; a list built in this order:
     - if `cmd` has a parent: `<parent.CommandPath()> - <parent.Short>`;
     - for each child of `cmd`, **sorted by name** (the child slice of `cmd`
       is sorted in place), skipping children that are not available
       (`!IsAvailableCommand()`, which also excludes `help`) or are additional
       help topics: `<child.Name()> - <child.Short>`.
     The separator is exactly space, hyphen, space.
3. Serialise the `cmdDoc` with `yaml.Marshal` (pass a pointer to it) and write
   the resulting bytes to `w` in a single write; return the error of that
   write (`nil` on success). Nothing else is written (no document separator, no
   auto-generated tag or date).
4. `linkHandler` is accepted for API compatibility and is **not** used.
5. If YAML marshalling fails (not expected for these plain types), print the
   error to standard output (`fmt.Println(err)`, not to `w` and not to
   stderr) and terminate the process with `os.Exit(1)`.

Example: for the test tree (root `root` with persistent flags `rootflag`/`r`
and `strtwo`/`t`; child `echo` with `Short "Echo anything to the screen"`,
`Long "an utterly useless command for testing"`,
`Example "Just run cobra-test echo"`, flags `boolone`/`b` etc., runnable
children `echosub` and `times` and a deprecated child), `GenYaml(echo, w)`
writes a document beginning

```yaml
name: root echo
synopsis: Echo anything to the screen
description: an utterly useless command for testing
options:
- name: boolone
  shorthand: b
  default_value: "true"
  usage: help message for flag boolone
- name: help
  shorthand: h
  default_value: "false"
  usage: help for echo
...
```

followed by `inherited_options` (`rootflag`, `strtwo`), `example`, and

```yaml
see_also:
- root - Root short description
- echosub - second sub command for echo
- times - Echo anything to the screen more times
```

## 3. Input specification

- `cmd`: non-nil `*cobra.Command` anywhere in a command tree.
- `w`: non-nil `io.Writer`.
- `linkHandler`: any function (may be nil, it is ignored).

## 4. Output specification

- Returns the error from writing to `w`, or `nil`.
- `w` receives exactly the bytes of `yaml.Marshal(&doc)`.

## 5. Edge cases and constraints

- Empty `Short`/`Long`/`Example` and empty option lists are omitted from the
  YAML (because of `omitempty`); `name` is always present.
- A root command without available, non-help-topic children has no
  `see_also` key. A sub-command always has at least the parent entry.
- `Short`/`Long` longer than 60 bytes without a newline get a trailing newline
  added (via `forceMultiLine`), which changes how YAML renders them.
- `cmd` may be modified as described (help command, help flag, child order).
  Calling twice yields identical output.
