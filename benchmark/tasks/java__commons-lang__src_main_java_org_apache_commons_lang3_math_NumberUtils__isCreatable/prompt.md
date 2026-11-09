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

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/math/NumberUtils.java`
- **Enclosing scope:** `public class NumberUtils`

## Imports / includes available in this file

```
import java.lang.reflect.Array;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.Validate;
```

## Other functions defined in the same file (signatures only; you may call them)

```
NumberUtils::NumberUtils()
NumberUtils::compare( final byte x , final byte y)
NumberUtils::compare( final int x , final int y)
NumberUtils::compare( final long x , final long y)
NumberUtils::compare( final short x , final short y)
NumberUtils::createBigDecimal( final String str)
NumberUtils::createBigInteger( final String str)
NumberUtils::createDouble( final String str)
NumberUtils::createFloat( final String str)
NumberUtils::createInteger( final String str)
NumberUtils::createLong( final String str)
NumberUtils::createNumber( final String str)
NumberUtils::getMantissa( final String str , final int stopPos)
NumberUtils::getMantissa( final String str)
NumberUtils::isAllZeros( final String str)
NumberUtils::isDigits( final String str)
NumberUtils::isNumber( final String str)
NumberUtils::isParsable( final String str)
NumberUtils::max( byte a , final byte b , final byte c)
NumberUtils::max( final byte ... array)
NumberUtils::max( final double ... array)
NumberUtils::max( final double a , final double b , final double c)
NumberUtils::max( final float ... array)
NumberUtils::max( final float a , final float b , final float c)
NumberUtils::max( final int ... array)
NumberUtils::max( final long ... array)
NumberUtils::max( final short ... array)
NumberUtils::max( int a , final int b , final int c)
NumberUtils::max( long a , final long b , final long c)
NumberUtils::max( short a , final short b , final short c)
NumberUtils::min( byte a , final byte b , final byte c)
NumberUtils::min( final byte ... array)
NumberUtils::min( final double ... array)
NumberUtils::min( final double a , final double b , final double c)
NumberUtils::min( final float ... array)
NumberUtils::min( final float a , final float b , final float c)
NumberUtils::min( final int ... array)
NumberUtils::min( final long ... array)
NumberUtils::min( final short ... array)
NumberUtils::min( int a , final int b , final int c)
NumberUtils::min( long a , final long b , final long c)
NumberUtils::min( short a , final short b , final short c)
NumberUtils::toByte( final String str , final byte defaultValue)
NumberUtils::toByte( final String str)
NumberUtils::toDouble( final BigDecimal value , final double defaultValue)
NumberUtils::toDouble( final BigDecimal value)
NumberUtils::toDouble( final String str , final double defaultValue)
NumberUtils::toDouble( final String str)
NumberUtils::toFloat( final String str , final float defaultValue)
NumberUtils::toFloat( final String str)
NumberUtils::toInt( final String str , final int defaultValue)
NumberUtils::toInt( final String str)
NumberUtils::toLong( final String str , final long defaultValue)
NumberUtils::toLong( final String str)
NumberUtils::toScaledBigDecimal( final BigDecimal value , final int scale , final RoundingMode roundingMode)
NumberUtils::toScaledBigDecimal( final BigDecimal value)
NumberUtils::toScaledBigDecimal( final Double value , final int scale , final RoundingMode roundingMode)
NumberUtils::toScaledBigDecimal( final Double value)
NumberUtils::toScaledBigDecimal( final Float value , final int scale , final RoundingMode roundingMode)
NumberUtils::toScaledBigDecimal( final Float value)
NumberUtils::toScaledBigDecimal( final String value , final int scale , final RoundingMode roundingMode)
NumberUtils::toScaledBigDecimal( final String value)
NumberUtils::toShort( final String str , final short defaultValue)
NumberUtils::toShort( final String str)
NumberUtils::validateArray( final Object array)
NumberUtils::withDecimalsParsing( final String str , final int beginIdx)
```

## Instance state

`isCreatable(String)` is a public static method of `NumberUtils`; it reads no fields or constants. The sibling `isNumber(String)` is a deprecated alias, and `isParsable(String)` is a stricter, separate method. `StringUtils.isEmpty(CharSequence)` and `StringUtils.contains(CharSequence, int)` are available.

=== STUB ===
```java
public static boolean isCreatable(final String str) {
    // TODO: implement according to the specification
}
```
