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

`Soundex.soundex(String str)` computes the Soundex code of a word: a four-character string made of the first letter of the word followed by three digits, describing how the rest of the word sounds. The letter-to-digit table and the treatment of the letters `H` and `W` depend on the `Soundex` instance (see "Instance state" in the context).

## 2. Functional requirements

1. `null` input returns `null`.
2. Clean the input: remove every character that is not a letter (`Character.isLetter`) and convert the rest to upper case with `Locale.ENGLISH`. The helper `SoundexUtils.clean(String)` of the same package does exactly this and may be called. If the cleaned string is empty, return it (the empty string).
3. The result has exactly four characters and starts with the first letter of the cleaned string. The remaining positions are filled with digit codes and padded with `'0'` characters.
4. Digit codes are obtained from the instance's mapping via the helper `map(char)` (which maps `'A'`..`'Z'` to a mapping character). Starting with the second letter of the cleaned string and moving left to right, until the four positions are filled:
   - If the instance treats `H` and `W` specially (see state), the letters `H` and `W` are skipped entirely: they produce no digit and do not change the "previous digit".
   - The code of the letter is looked up with `map`. If it is the silent marker `'-'`, the letter is skipped (it produces no digit and does not change the "previous digit" either).
   - A code is appended to the result only if it is not `'0'` and differs from the "previous digit". The "previous digit" is then set to this code. A `'0'` code (a vowel in the default table) is not appended but does become the "previous digit", so equal codes separated by a vowel are both kept.
   - The "previous digit" starts as the code of the first letter (even though the first letter itself is emitted as a letter).
5. Letters outside `A`..`Z` (for example `'É'`) are not mapped: `map` throws `IllegalArgumentException` with a message of the form `The character is not mapped: <char> (index=<n>)` where `<n>` is `char - 'A'`. This happens for any such letter that is examined (including the first letter), so the exception can only be avoided for letters after the fourth output position is already filled.

## 3. Input specification

Any string or `null`.

## 4. Output specification

A 4-character string, the empty string, or `null` as described. Examples with the default instance: `"Robert"` -> `R163`; `"Rupert"` -> `R163`; `"Rubin"` -> `R150`; `"Ashcraft"` -> `A261`; `"Tymczak"` -> `T522`; `"Pfister"` -> `P236`; `"Lee"` -> `L000`; `"A"` -> `A000`; `"  "` -> `""`.

## 5. Edge cases and constraints

- The method reads only immutable instance state, so it is thread-safe.
- Input case and non-letter characters (digits, spaces, punctuation) do not matter.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/Soundex.java`
- **Enclosing scope:** `public class Soundex implements StringEncoder`

## Imports / includes available in this file

```
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringEncoder;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Soundex::Soundex( final String mapping , final boolean specialCaseHW)
Soundex::Soundex( final String mapping)
Soundex::Soundex( final char [ ] mapping)
Soundex::Soundex()
Soundex::difference( final String s1 , final String s2)
Soundex::encode( final Object obj)
Soundex::encode( final String str)
Soundex::getMaxLength()
Soundex::hasMarker( final char [ ] mapping)
Soundex::map( final char ch)
Soundex::setMaxLength( final int maxLength)
```

## Instance state

- `soundexMapping` (`char[]`, private final): for each letter `'A'`+i, the code character. Default (US English) table string: `"01230120022455012623010202"` (`'0'` = vowel-like/not coded). A mapping may contain the marker `SILENT_MARKER = '-'` (public static final char) for "ignore this letter".
- `specialCaseHW` (`boolean`, private final): `true` if the instance skips `H` and `W` completely. It is `true` for `new Soundex()` and `Soundex.US_ENGLISH`; for `new Soundex(char[] mapping)` / `new Soundex(String mapping)` it is `true` unless the mapping contains `SILENT_MARKER`; `Soundex.US_ENGLISH_SIMPLIFIED` (mapping `"01230120022455012623010202"`) uses `false`; `Soundex.US_ENGLISH_GENEALOGY` (mapping `"-123-12--22455-12623-1-2-2"`) uses `false` because its mapping has silent markers.
- `private char map(char ch)`: returns `soundexMapping[ch - 'A']` or throws `IllegalArgumentException("The character is not mapped: " + ch + " (index=" + (ch - 'A') + ")")` when the index is outside the table.
- `SoundexUtils.clean(String)` (package-private static): keeps letters only, upper-cases with `Locale.ENGLISH`.

=== STUB ===
```java
public String soundex(String str) {
    // TODO: implement according to the specification
}
```
