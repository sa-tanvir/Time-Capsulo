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
