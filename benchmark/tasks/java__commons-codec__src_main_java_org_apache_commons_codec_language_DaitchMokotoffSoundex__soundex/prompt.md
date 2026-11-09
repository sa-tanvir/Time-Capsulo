You are an expert Java developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Java code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```java code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/DaitchMokotoffSoundex.java`
- **Enclosing scope:** `public class DaitchMokotoffSoundex implements StringEncoder`

## Imports / includes available in this file

```
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;
import org.apache.commons.codec.CharEncoding;
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.Resources;
import org.apache.commons.codec.StringEncoder;
```

## Other functions defined in the same file (signatures only; you may call them)

```
DaitchMokotoffSoundex::Branch::Branch()
DaitchMokotoffSoundex::Branch::createBranch()
DaitchMokotoffSoundex::Branch::equals( final Object other)
DaitchMokotoffSoundex::Branch::finish()
DaitchMokotoffSoundex::Branch::hashCode()
DaitchMokotoffSoundex::Branch::processNextReplacement( final String replacement , final boolean forceAppend)
DaitchMokotoffSoundex::Branch::toString()
DaitchMokotoffSoundex::DaitchMokotoffSoundex( final boolean folding)
DaitchMokotoffSoundex::DaitchMokotoffSoundex()
DaitchMokotoffSoundex::Rule::Rule( final String pattern , final String replacementAtStart , final String replacementBeforeVowel , final String replacementDefault)
DaitchMokotoffSoundex::Rule::getPatternLength()
DaitchMokotoffSoundex::Rule::getReplacements( final String context , final boolean atStart)
DaitchMokotoffSoundex::Rule::isVowel( final char ch)
DaitchMokotoffSoundex::Rule::matches( final String context)
DaitchMokotoffSoundex::Rule::toString()
DaitchMokotoffSoundex::cleanup( final String input)
DaitchMokotoffSoundex::encode( final Object obj)
DaitchMokotoffSoundex::encode( final String source)
DaitchMokotoffSoundex::for( final Map . Entry<Character,List<Rule>> rule : RULES . entrySet())
DaitchMokotoffSoundex::parseRules( final Scanner scanner , final String location , final Map<Character,List<Rule>> ruleMapping , final Map<Character,Character> asciiFoldings)
DaitchMokotoffSoundex::soundex( final String source)
DaitchMokotoffSoundex::stripQuotes( String str)
DaitchMokotoffSoundex::try( final Scanner scanner = new Scanner(Resources.getInputStream(RESOURCE_FILE),CharEncoding.UTF_8))
```

## Instance state and helpers

- `folding` (`boolean`, private final): whether `cleanup` folds accented/special letters to base letters using the `FOLDINGS` table (`Map<Character, Character>`). `new DaitchMokotoffSoundex()` folds; `new DaitchMokotoffSoundex(false)` does not.
- `private static final int MAX_LENGTH = 6`: number of code digits.
- `RULES`: `private static final Map<Character, List<Rule>>` (static, built from the resource file `org/apache/commons/codec/language/dmrules.txt`): for each lower-case character, the list of rules, sorted so that longer patterns come first.
- `private String cleanup(String)`: removes whitespace characters, lower-cases each character with `Character.toLowerCase`, and applies `FOLDINGS` when `folding` is true.
- `private static final class Rule`: `getPatternLength()`, `matches(String context)` (true if `context.startsWith(pattern)`), `getReplacements(String context, boolean atStart)` returns the alternatives (a `String[]`) for the rule: the "at start" alternatives if `atStart`, else the "before vowel" ones when the character following the pattern in `context` is one of `a e i o u`, else the default ones.
- `private static final class Branch` (one partial code): `new Branch()` empty; `createBranch()` copy; `processNextReplacement(String replacement, boolean forceAppend)` appends the replacement unless the previous replacement of this branch ends with the same text (and `forceAppend` is false) or the branch already has `MAX_LENGTH` digits (it truncates at `MAX_LENGTH` and remembers the replacement as last); `finish()` pads with `'0'` up to `MAX_LENGTH`; `toString()` is the code; `equals`/`hashCode` are based on the code string.
- Imports available include `java.util.ArrayList`, `Collections`, `LinkedHashSet`, `List`, `Map`, `Set`.

=== STUB ===
```java
private String[] soundex(final String source, final boolean branching) {
    // TODO: implement according to the specification
}
```
