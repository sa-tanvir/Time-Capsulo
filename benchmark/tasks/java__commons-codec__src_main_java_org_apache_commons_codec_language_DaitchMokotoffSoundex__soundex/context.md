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
