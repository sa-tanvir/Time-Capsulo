# Functional specification

## 1. Component overview

`DaitchMokotoffSoundex.soundex(String source, boolean branching)` (private) is the engine of the Daitch-Mokotoff Soundex encoder, a phonetic code for (mostly Slavic and Germanic) surnames. The public method `soundex(String)` calls it with `branching = true` and joins the result with `|`; the public method `encode(String)` calls it with `branching = false` and returns the first result. The method returns the array of all alternative six-digit codes for the name.

## 2. Functional requirements

1. A `null` source returns `null`.
2. The source is first normalised with the existing helper `cleanup(String)` (whitespace removed, lower-cased, and optionally folded to ASCII letters depending on the instance).
3. The normalised name is processed from left to right, starting with one empty code branch. For the character at position `index`:
   - Whitespace characters are skipped (and do not change the "last character").
   - The list of rules registered for the character is taken from the rule table (`RULES`). If the table has no entry for the character (for example digits, punctuation or letters without a rule), the character is skipped and does not change the "last character".
   - Otherwise the rules of the list are tried in order; the first rule whose pattern matches the remaining text starting at `index` (`Rule.matches(remaining)`) is used. It yields its replacement alternatives via `Rule.getReplacements(remaining, atStart)`, where `atStart` is true if no earlier character has been processed yet (the "last character" is still unset).
   - After a rule was applied, scanning continues after the whole pattern (the index advances by the pattern length).
   - If the character has a rule list but no rule matches, nothing is appended and scanning advances by one character.
   - Whenever the character was not skipped (a rule list existed, whether a rule matched or not), the "last character" becomes the character at `index` (the first character of the pattern).
4. Applying a replacement to a branch is done with `Branch.processNextReplacement(replacement, force)`, where `force` is true when the last character and the current character are `m`,`n` or `n`,`m` (in either order). The branch itself ignores repeated codes and enforces the maximum code length.
5. In **branching** mode: when the rule yields more than one alternative, every current branch is duplicated once per alternative (using `Branch.createBranch()`, so the original branch is not modified), and every alternative is applied to its own branch copy; with exactly one alternative the existing branches are updated in place. The set of current branches is then replaced by the resulting branches, **in order**, and identical branches (same code string) are merged (set semantics, insertion order kept).
6. In **non-branching** mode only the first alternative of each rule is applied and only one branch ever exists.
7. At the end every branch is padded (`Branch.finish()`) to the full code length and its string is returned. The result array has one element per remaining distinct branch, in branch order.

## 3. Input specification

`source`: any string or `null`. Characters for which the instance has no rules are ignored.

## 4. Output specification

A `String[]` of six-character digit codes (one element in non-branching mode, one or more in branching mode), or `null`. Examples (default instance): the public `soundex("Peterson")` yields `734600|739460` (two branches) and `encode("Peterson")` yields `734600` (first alternative only); `soundex("Jackson")` yields `154600|145460|454600|445460`; `soundex("Auerbach")` yields `097400|097500`; `encode("Moskowitz")` yields `645740`. (The exact strings follow from the rule table.)

## 5. Edge cases and constraints

- Empty or whitespace-only input yields a single code of six zeros (`"000000"`).
- The method does not modify any shared state; the rule table is read-only.
