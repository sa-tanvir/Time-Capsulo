# Functional specification: `func hasSeeAlso(cmd *cobra.Command) bool`

## 1. Component overview

Package `doc` (`github.com/spf13/cobra/doc`) generates documentation (man
pages, Markdown, reStructuredText, YAML) for cobra command trees. Each
generated page may end with a "SEE ALSO" section that links to the parent
command and to the visible sub-commands. `hasSeeAlso` decides whether such a
section is needed for command `cmd`: it reports whether there is at least one
command worth linking to.

## 2. Functional requirements

Return `true` if and only if at least one of the following holds:

1. `cmd` has a parent command (`cmd.HasParent()`); a sub-command always links
   back to its parent.
2. `cmd` has at least one child command `c` (among `cmd.Commands()`) such that
   `c.IsAvailableCommand()` is true **and** `c.IsAdditionalHelpTopicCommand()`
   is false.

Otherwise return `false`. In particular a root command (no parent) with no
children, or whose children are all hidden, deprecated, its auto-generated
`help` command, not runnable without available sub-commands, or additional
help topics, has no "SEE ALSO" section.

The function only inspects the command tree. It has no other side effects
(apart from `Commands()` sorting the child list in place, which is the normal
behaviour of that accessor).

Examples:

| command | result |
|---|---|
| root with no children | false |
| any sub-command (has a parent), even without children | true |
| root with one runnable, visible child | true |
| root whose only children are hidden or deprecated | false |
| root whose only child is the auto-generated `help` command | false |
| root whose only child is not runnable and has no children (a help topic) | false |
| root with a non-runnable child that has a runnable visible grandchild | true |
| root with children `aaa` (hidden), `bbb` (runnable) | true |

## 3. Input specification

- `cmd`: a non-nil `*cobra.Command`, part of an arbitrary command tree (any
  depth and fan-out).

## 4. Output specification

- A `bool` as defined above.

## 5. Edge cases and constraints

- A child counts only if it is available **and** not an additional help topic.
- Having a parent is sufficient on its own, regardless of children.
- Deterministic; does not modify any command's fields.
