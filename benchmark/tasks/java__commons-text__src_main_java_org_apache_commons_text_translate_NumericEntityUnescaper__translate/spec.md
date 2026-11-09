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
