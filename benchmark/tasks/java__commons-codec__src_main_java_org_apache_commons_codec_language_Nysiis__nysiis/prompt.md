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

`Nysiis.nysiis(String str)` computes the NYSIIS (New York State Identification and Intelligence System) phonetic code of a name. The result is an upper-case string of letters. When the encoder was created as "strict" (see `isStrict()`) the code is truncated to 6 characters.

## 2. Functional requirements

1. `null` input returns `null`.
2. The input is first cleaned: all characters that are not letters are removed and the rest is converted to upper case (`Locale.ENGLISH`). The cleaning helper `SoundexUtils.clean(String)` of the same package does exactly this and may be called. If nothing remains, the (empty) cleaned string is returned.
3. Start-of-name translations, applied to the cleaned string in this order (each only at the very beginning of the string): `MAC` -> `MCC`; `KN` -> `NN`; `K` -> `C`; `PH` or `PF` -> `FF`; `SCH` -> `SSS`.
4. End-of-name translations, applied afterwards (only at the very end): `EE` or `IE` -> `Y`; then `DT`, `RT`, `RD`, `NT` or `ND` -> `D`.
5. The first character of the (translated) string always starts the key. Every following character, left to right, is transcoded by the existing helper `transcodeRemaining(prev, curr, next, aNext)`, where `prev` is the character at the preceding position **in the working string as already modified by earlier transcodings**, `curr` is the current character, and `next` / `aNext` are the one and two following characters of the working string (a space where the string ends). The helper returns one or more characters; they overwrite the working string starting at the current position (so a multi-character replacement such as `EV` -> `AF`, `KN` -> `NN`, `SCH` -> `SSS` or `PH` -> `FF` overwrites the following positions, and those positions are later transcoded from their new values). After transcoding, the character now at the current position is appended to the key only if it differs from the character at the preceding position of the working string.
6. Final clean-up of the key, only when it has more than one character, in this order: if the last character is `S` it is removed; if the (new) key then has more than two characters and ends with `AY`, the `A` is removed (the key then ends with `Y`); if the last character is now `A`, it is removed.
7. In strict mode the result is cut to at most 6 characters; in non-strict mode its length is unlimited.

## 3. Input specification

Any string or `null`; non-letters are ignored, letters (including non-ASCII letters) are kept.

## 4. Output specification

The key as an upper-case string; `null` for `null`; empty string for input without letters. Examples (default strict encoder): `"Macintosh"` -> `MCANT`; `"Knight"` -> `NAGT`; `"Phillips"` -> `FALAP`; `"Smith"` -> `SNAT`; `"Bobbie"` -> `BABY`; `"Wright"` -> `WRAGT`; `"Schmidt"` -> `SNAD`; `"Bartholomew"` -> `BARTAL` (strict, cut to 6 characters) but `BARTALAN` with a non-strict encoder; `"A"` -> `A`.

## 5. Edge cases and constraints

- Does not modify any state; independent of the default locale.
- A one-character key (for example from `"A"`) is returned unchanged; the clean-up in rule 6 does not apply to keys of length 1.
- Input like `"123"` (no letters) gives `""`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/codec/language/Nysiis.java`
- **Enclosing scope:** `public class Nysiis implements StringEncoder`

## Imports / includes available in this file

```
import java.util.regex.Pattern;
import org.apache.commons.codec.EncoderException;
import org.apache.commons.codec.StringEncoder;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Nysiis::Nysiis( final boolean strict)
Nysiis::Nysiis()
Nysiis::encode( final Object obj)
Nysiis::encode( final String str)
Nysiis::isStrict()
Nysiis::isVowel( final char c)
Nysiis::transcodeRemaining( final char prev , final char curr , final char next , final char aNext)
```

=== STUB ===
```java
public String nysiis(String str) {
    // TODO: implement according to the specification
}
```
