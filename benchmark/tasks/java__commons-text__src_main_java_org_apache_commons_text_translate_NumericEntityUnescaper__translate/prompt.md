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

`NumericEntityUnescaper.translate(input, index, out)` recognises an HTML/XML numeric character reference such as `&#65;` (decimal) or `&#x41;` / `&#X41;` (hexadecimal) that starts exactly at position `index` of `input`, writes the corresponding character (or surrogate pair) to `out`, and tells the caller how many input characters it consumed. It is the per-position step of a translator that unescapes a whole string.

## 2. Functional requirements

1. A reference is only considered if `input.charAt(index) == '&'`, `index < input.length() - 2` (there must be at least one more character after `&#`), and `input.charAt(index + 1) == '#'`. Otherwise return `0` and write nothing.
2. After `&#`: if the next character is `x` or `X`, the number is hexadecimal and the digits start after it; if the input ends right after the `x`/`X` (no character follows), return `0`. Otherwise the number is decimal.
3. The digit run is the longest sequence of characters from `0-9`, `a-f`, `A-F` starting at the first digit position, ending at the end of the input at the latest. Letters `a-f` are collected even for decimal references.
4. A semicolon is "present" if the digit run ends before the end of the input and the next character is `;`.
5. If the semicolon is not present: if the option `semiColonRequired` is set (`isSet`), return `0` (nothing written); otherwise, if `errorIfNoSemiColon` is set, throw `IllegalArgumentException` with the message `Semi-colon required at end of numeric entity`. Otherwise (neither option set) the reference is accepted without semicolon. The `semiColonRequired` test comes first.
6. Parse the digit run as an integer in base 16 (hexadecimal) or base 10. If it cannot be parsed (empty digit run, letters in a decimal run, or a value too large for `int`) return `0` and write nothing.
7. If the parsed value is above `0xFFFF`, write the UTF-16 surrogate pair of that code point (high surrogate first); a value above `0x10FFFF` is not a valid code point and the resulting `IllegalArgumentException` from the character conversion propagates. Otherwise write the single `char` with that numeric value (value 0 writes the char `'\u0000'`).
8. Return the number of input characters consumed: `2` for `&#`, plus `1` for the `x`/`X` if hexadecimal, plus the number of digits, plus `1` if the semicolon is present (the semicolon is consumed only when present).

## 3. Input specification

`input`: any non-null `CharSequence`; `index`: `0 <= index < input.length()`; `out`: a non-null `Writer`. The instance options are as in the context.

## 4. Output specification

Returns an `int >= 0` as above; writes at most one character or surrogate pair to `out`. Examples (default options): `("&#65;", 0)` writes `A` and returns 5; `("&#x41;", 0)` writes `A`, returns 6; `("&#68642;", 0)` writes the two chars `𐰢`, returns 8; `("&#65", 0)` returns 0 (semicolon required); with `semiColonOptional`, `("&#65", 0)` writes `A` and returns 4; `("&#", 0)` and `("&#x", 0)` return 0; `("&#xZZ;", 0)` returns 0; `("A&#65;", 1)` writes `A`, returns 5; any position that is not `&` returns 0.

## 5. Edge cases and constraints

- No exception other than those described may escape for the inputs in section 3 (in particular no `StringIndexOutOfBoundsException` for entities cut off at the end of the input).
- Nothing is written when `0` is returned.
- The method does not modify `input` or the options.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/translate/NumericEntityUnescaper.java`
- **Enclosing scope:** `public enum OPTION { semiColonRequired, semiColonOptional, errorIfNoSemiColon }`

## Imports / includes available in this file

```
import java.io.IOException;
import java.io.Writer;
import java.util.Arrays;
import java.util.EnumSet;
```

## Other functions defined in the same file (signatures only; you may call them)

```
NumericEntityUnescaper::NumericEntityUnescaper( final OPTION ... options)
NumericEntityUnescaper::isSet( final OPTION option)
```

## Instance state

- `options` (`private final EnumSet<OPTION>`): the options chosen at construction. The constructor `NumericEntityUnescaper(OPTION... options)` stores the given options, or `{semiColonRequired}` if none were given.
- `OPTION` is the public nested enum with the constants `semiColonRequired`, `semiColonOptional`, `errorIfNoSemiColon`.
- `isSet(OPTION option)` returns whether `option` is in `options`.

`translate(CharSequence input, int index, Writer out)` is the abstract method of the parent class `CharSequenceTranslator`: it examines `input` at `index`, may write a replacement to `out`, and returns the number of `char`s of `input` consumed (0 if nothing was translated, in which case nothing may be written).

=== STUB ===
```java
public int translate(final CharSequence input, final int index, final Writer out) throws IOException {
    // TODO: implement according to the specification
}
```
