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

`DoubleMetaphone.doubleMetaphone(String value, boolean alternate)` computes the Double Metaphone phonetic key of a word or name (Lawrence Philips' algorithm, as implemented by Apache Commons Codec). Every word has a primary key and possibly a different alternate key (a second plausible pronunciation). The method returns one of them, selected by `alternate`. The key is an upper-case string of consonant codes such as `K`, `S`, `X`, `0` (the "th" sound), `J`, `F`, `P`, `N`, `M`, `L`, `R`, `T`, `A`.

The class also provides per-letter rule handling that the character-by-character scan is expected to use: `handleAEIOUY`, `handleC`, `handleD`, `handleG`, `handleH`, `handleJ`, `handleL`, `handleP`, `handleR`, `handleS`, `handleT`, `handleW`, `handleX`, `handleZ`, `conditionM0`, `isSlavoGermanic`, `isSilentStart`, `cleanInput` and a result accumulator `DoubleMetaphoneResult` (see context). You may call them. Their behaviour must not be re-implemented differently; this method decides which one is applied at each position and how far to advance.

## 2. Functional requirements

1. Normalise the input (leading and trailing whitespace removed, converted to upper case with `Locale.ENGLISH`). If the input is `null`, or is empty after trimming, return `null`.
2. Determine once, from the whole normalised word, whether it is "Slavo-Germanic", and whether it starts with a silent letter pair (`GN`, `KN`, `PN`, `WR`, `PS`); if so, scanning starts at the second character, otherwise at the first.
3. Create a key accumulator limited to `getMaxCodeLen()` characters (default 4). Scan the word from the start index; stop as soon as both the primary and the alternate keys have reached the maximum length, or the end of the word is reached.
4. At each position, the current letter decides the action:
   - `A E I O U Y`: vowel handling (delegated) which returns the next index.
   - `B`: append `P`; skip a following `B` as well.
   - `Ç` (C with cedilla): append `S`, advance by one.
   - `C`, `D`, `G`, `H`, `J`, `L`, `P`, `R`, `S`, `T`, `W`, `X`, `Z`: apply the corresponding per-letter rule, which returns the next index. `G`, `J`, `R`, `S` and `Z` also receive the Slavo-Germanic flag.
   - `F`: append `F`; `K`: append `K`; `N`: append `N`; `Q`: append `K`; `V`: append `F`. In each of these cases a doubled letter (the same letter at the next position) is consumed together with the first.
   - `M`: append `M`; advance by two when the special "M" condition holds (an `M` directly followed by `M`, or the "UMB" ending pattern), otherwise by one.
   - `Ñ` (N with tilde): append `N`, advance by one.
   - Any other character (digits, punctuation, other letters): ignored, advance by one.
5. Return the alternate key if `alternate` is `true`, otherwise the primary key.

## 3. Input specification

- `value`: any string, possibly `null`, empty or whitespace-only; may contain non-letters and the characters `Ç` / `Ñ`.
- `alternate`: selects the key to return.

## 4. Output specification

- The primary or alternate key, an upper-case string of at most `getMaxCodeLen()` characters, or `null` for null/blank input.
- Examples (primary / alternate): `"testing"` -> `TSTN` / `TSTN`; `"The"` -> `0` / `T`; `"quick"` -> `KK`; `"brown"` -> `PRN`; `"fox"` -> `FKS`; `"jumped"` -> `JMPT` / `AMPT`; `"MacCafferey"` -> `MKFR`; `"Stephan"` -> `STFN`; `"san jose"` -> `SNHS`; `"ç"` -> `S`; `"ñ"` -> `N`.
- `null`, `""`, `" "` and `"\t\n\r "` all return `null`.

## 5. Edge cases and constraints

- The result does not depend on the default locale.
- With `setMaxCodeLen(n)`, keys are cut to at most `n` characters.
- The method has no side effects on the object (the code length limit is only read).

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/DoubleMetaphone.java`
- **Enclosing scope:** `public class DoubleMetaphone implements StringEncoder`

## Imports / includes available in this file

```
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringEncoder;
import org.apache.commons.codec.binary.StringUtils;
```

## Other functions defined in the same file (signatures only; you may call them)

```
DoubleMetaphone::DoubleMetaphone()
DoubleMetaphone::DoubleMetaphoneResult::DoubleMetaphoneResult( final int maxLength)
DoubleMetaphone::DoubleMetaphoneResult::append( final String primary , final String alternate)
DoubleMetaphone::DoubleMetaphoneResult::append( final String value)
DoubleMetaphone::DoubleMetaphoneResult::append( final char primary , final char alternate)
DoubleMetaphone::DoubleMetaphoneResult::append( final char value)
DoubleMetaphone::DoubleMetaphoneResult::appendAlternate( final String value)
DoubleMetaphone::DoubleMetaphoneResult::appendAlternate( final char value)
DoubleMetaphone::DoubleMetaphoneResult::appendPrimary( final String value)
DoubleMetaphone::DoubleMetaphoneResult::appendPrimary( final char value)
DoubleMetaphone::DoubleMetaphoneResult::getAlternate()
DoubleMetaphone::DoubleMetaphoneResult::getPrimary()
DoubleMetaphone::DoubleMetaphoneResult::isComplete()
DoubleMetaphone::charAt( final String value , final int index)
DoubleMetaphone::cleanInput( String input)
DoubleMetaphone::conditionC0( final String value , final int index)
DoubleMetaphone::conditionCH0( final String value , final int index)
DoubleMetaphone::conditionCH1( final String value , final int index)
DoubleMetaphone::conditionL0( final String value , final int index)
DoubleMetaphone::conditionM0( final String value , final int index)
DoubleMetaphone::contains( final String value , final int start , final int length , final String ... criteria)
DoubleMetaphone::doubleMetaphone( final String value)
DoubleMetaphone::encode( final Object obj)
DoubleMetaphone::encode( final String value)
DoubleMetaphone::getMaxCodeLen()
DoubleMetaphone::handleAEIOUY( final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleC( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleCC( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleCH( final String value , final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleD( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleG( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleGH( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleH( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleJ( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleL( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleP( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleR( final String value , final DoubleMetaphoneResult result , final int index , final boolean slavoGermanic)
DoubleMetaphone::handleS( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::handleSC( final String value , final DoubleMetaphoneResult result , final int index)
DoubleMetaphone::handleT( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleW( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleX( final String value , final DoubleMetaphoneResult result , int index)
DoubleMetaphone::handleZ( final String value , final DoubleMetaphoneResult result , int index , final boolean slavoGermanic)
DoubleMetaphone::isDoubleMetaphoneEqual( final String value1 , final String value2 , final boolean alternate)
DoubleMetaphone::isDoubleMetaphoneEqual( final String value1 , final String value2)
DoubleMetaphone::isSilentStart( final String value)
DoubleMetaphone::isSlavoGermanic( final String value)
DoubleMetaphone::isVowel( final char ch)
DoubleMetaphone::setMaxCodeLen( final int maxCodeLen)
```

## Instance state

- `maxCodeLen` (`int`, private, default 4): maximum length of each key; read through `getMaxCodeLen()`, changed with `setMaxCodeLen(int)`.
- Constants: `VOWELS = "AEIOU"`, `SILENT_START = {"GN", "KN", "PN", "WR", "PS"}` (used by `isSilentStart`).
- `DoubleMetaphoneResult` (inner class): `new DoubleMetaphoneResult(int maxLength)`; `append(char)` / `append(char, char)` / `append(String)` / `append(String, String)` add to both keys (or to primary and alternate separately); `appendPrimary`, `appendAlternate`; `getPrimary()`, `getAlternate()`; `isComplete()` is true once both keys have reached `maxLength`. Appending never makes a key longer than `maxLength`.
- Each `handleX(...)` helper takes the (normalised) word, the result accumulator and the current index (plus the Slavo-Germanic flag for G, J, R, S, Z) and returns the next index to examine. `handleAEIOUY(result, index)` takes no word.
- `charAt(value, index)` returns `Character.MIN_VALUE` for out-of-range indexes.

=== STUB ===
```java
public String doubleMetaphone(String value, final boolean alternate) {
    // TODO: implement according to the specification
}
```
