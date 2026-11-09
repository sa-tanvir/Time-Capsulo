# Functional specification

## 1. Component overview

`NumberUtils.isCreatable(str)` reports whether a string is a valid Java-style number literal: decimal numbers with optional sign, decimal point, exponent and type suffix, plus hexadecimal (`0x`/`0X`) and octal (leading `0`) integers.

## 2. Functional requirements

Return `false` for `null` or the empty string. Otherwise let `start` be `1` if the first character is `-` or `+`, else `0`. The remaining text (after the optional sign) is checked as follows; the first applicable rule decides.

1. **Hex / octal.** If the text after the sign has at least two characters, begins with `0`, **and the whole string contains no `.`**:
   - if the second character is `x` or `X`: valid only if at least one character follows and all following characters are hex digits (`0-9`, `a-f`, `A-F`); no sign, suffix or other character is accepted (`"0x"` is false, `"0x1FL"` is false);
   - else if the second character is a decimal digit: valid only if every character from the second on is an octal digit `0-7` (so `"0123"` and `"00"` are true, `"09"`, `"08e1"` and `"01L"` are false);
   - otherwise (e.g. `"0e1"`, `"0f"`, `"0L"`) continue with rule 2.
2. **Decimal.** The text must have the shape
   `digits [ "." [digits] ] [ exponent ] [ suffix ]` or `"." digits [ exponent ] [ suffix ]`, where
   - there is at most one `.`, and it may not come after an exponent; `"5."` is valid, `"."` is not, `".5"` is valid; at least one digit must appear before the exponent or suffix;
   - `exponent` is `e` or `E`, an optional `+` or `-`, and one or more digits; an exponent needs at least one digit before it (`"e5"` is false, `"1e"`, `"1e+"` and `"1.5e"` are false), at most one exponent is allowed, and signs are only allowed at the very start and directly after the `e`/`E`;
   - `suffix` is a single character at the very end: `d`, `D`, `f`, `F` (allowed after any complete number, with or without decimal point/exponent, but only if at least one digit appeared, e.g. `"5.d"` true, `".d"` false, `"1e5f"` true), or `l`, `L` (allowed only if the number has no decimal point and no exponent: `"12L"` true, `"-1l"` true, `"1.5L"` false, `"1e5L"` false);
   - nothing else is allowed anywhere (no whitespace, no second suffix, no sign elsewhere): `"1.2.3"`, `"12a"`, `"1-"`, `"--1"`, `"1d5"`, `"1ff"` are false.

## 3. Input specification

`str`: `String` or `null`; any characters.

## 4. Output specification

A `boolean`. Examples: `"12"`, `"-12"`, `"+12"`, `"1.5"`, `".5"`, `"5."`, `"1e5"`, `"1.5E-3"`, `"1e+5"`, `"2.5f"`, `"12L"`, `"0xFF"`, `"-0Xff"`, `"0777"`, `"0e1"`, `"00.5"` -> `true`; `null`, `""`, `" "`, `"-"`, `"."`, `"e5"`, `"1e"`, `"0x"`, `"0xG"`, `"09"`, `"1.5L"`, `"1.2.3"`, `"1_000"` -> `false`.

## 5. Edge cases and constraints

- Pure function, no exceptions for any input. Very long strings (hundreds of thousands of characters) must be handled in linear time.
- A leading `0` check is made on the text after the sign (`"-0x1F"` and `"+0x1F"` are true).
