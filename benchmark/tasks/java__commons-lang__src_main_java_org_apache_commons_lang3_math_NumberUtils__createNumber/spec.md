# Functional specification

## 1. Component overview

`NumberUtils.createNumber(str)` converts a string that looks like a Java numeric literal into the `Number` subclass that best fits it: `Integer`, `Long`, `BigInteger`, `Float`, `Double` or `BigDecimal`. It also understands hexadecimal and octal notation, an explicit sign, scientific notation and the type suffixes `L`/`l`, `F`/`f`, `D`/`d`.

## 2. Functional requirements

Rules are applied in this order.

1. `null` -> return `null`. A blank string (empty or only whitespace) -> `NumberFormatException` with the message `A blank string is not a valid number`.
2. **Hexadecimal.** If `str` starts with one of `0x`, `0X`, `-0x`, `-0X`, `#`, `-#` (a leading `+` is not recognised), it is hexadecimal. Skip leading `0` characters after the prefix; let `h` be the number of remaining characters (all of them are counted, whatever they are) and `c` the first remaining character. If `h > 16`, or `h == 16` and `c > '7'` (compared as a character), return `createBigInteger(str)`. Otherwise, if `h > 8`, or `h == 8` and `c > '7'`, return `createLong(str)`. Otherwise return `createInteger(str)`. Whatever those helpers throw (a `NumberFormatException` for non-hex characters, for a prefix with no digits, etc.) propagates. Sign and prefix are handled by the helpers.
3. If `str` contains both an `e` and an `E` (and was not hexadecimal), throw `NumberFormatException`.
4. **Type-suffixed numbers.** Let `last` be the last character. If `last` is not a digit and not `.`, the string must end with a type suffix, otherwise (`last` not one of `lLfFdD`) throw `NumberFormatException` with the message `<str> is not a valid number.`. Let `numeric` be `str` without its last character. If `str` contains both a `.` and an `e`/`E` and the `e`/`E` comes before the `.`, throw `NumberFormatException` with the message `<str> is not a valid number.` (this check also applies to strings without suffix). Define the following values (they are used for the `L` check and the "all zeros" flag):
   - "has decimal point": `str` contains a `.`. "has exponent marker": `str` contains an `e` or `E` (at any position, it is then unique).
   - **exponent string**: if there is no `e`/`E` in `str`, the exponent is absent (treated as all zeros for the flag). Otherwise it is the text between the `e`/`E` and the suffix character (the last character, excluded). With a suffix present the `e`/`E` can never be the last character (that would make the last character `e`/`E`, which is not a valid suffix and fails), so the exponent can be the empty string, e.g. `"1.0e"` + `"f"` = `"1.0ef"`: the exponent is `""` (present, empty, NOT all zeros). `"1e5f"` has exponent `"5"`, `"1e0d"` has exponent `"0"`.
   - **mantissa**: if `str` has a `.`: the text before the first `.`; else if `str` has an `e`/`E`: the text before it; else (no `.` and no `e`/`E`, e.g. `"0f"`, `"123L"`) the **whole `str` including the suffix character**. In all cases one leading `+` or `-` is dropped first. The mantissa can be empty (e.g. `".5f"`).
   - The "all zeros" flag is true when the mantissa is a non-empty string consisting only of `0` characters AND the exponent is absent or a non-empty string of only `0` characters. Consequences: `"0f"`, `"00d"`, `"-0D"` have mantissa `"0f"` etc. (suffix included), so the flag is false for them: the float is `0.0` with flag false, so it is rejected, then the double is rejected the same way, and `createBigDecimal(numeric)` is returned (`"0f"` -> `BigDecimal 0`, `"0d"` -> `BigDecimal 0`). By contrast `"0.0f"` -> `Float 0.0`, `"0.0d"` -> `Double 0.0`, `"0e0f"` -> `Float 0.0`, `".0f"` (empty mantissa) -> flag false, `BigDecimal`.
   - `l`/`L`: only valid if `str` has no `.`, no `e`/`E` at all, and `numeric` is an optional leading `-` followed by one or more decimal digits (a leading `+` is not accepted). Return `createLong(numeric)`; if that throws `NumberFormatException` (e.g. too large) return `createBigInteger(numeric)`. Otherwise throw `NumberFormatException` with the message `<str> is not a valid number.`.
   - `f`/`F`: try `createFloat(str)`; accept it (return the `Float`) if it is not infinite and it is not `0.0` while the digits are not all zeros. If it is rejected or the conversion fails, fall through to the `double` handling.
   - `d`/`D` (and the fall-through from `f`/`F`): try `createDouble(str)`; accept it (return the `Double`) if it is not infinite and its `float` value is not `0.0` while the digits are not all zeros (note: the zero test is applied to the `double` converted to `float`). Otherwise try `createBigDecimal(numeric)` and return it. If everything fails, throw `NumberFormatException` with the message `<str> is not a valid number.`.
5. **Integers without suffix.** If `last` is a digit or `.`: if the string has no `.` and no exponent, try `createInteger(str)`; on `NumberFormatException` try `createLong(str)`; on `NumberFormatException` return `createBigInteger(str)` (its exception, if any, propagates). Note that these helpers interpret a leading `0` as octal and accept `0x`/`#` prefixes, so e.g. `"0123"` is 83 and `"09"` throws `NumberFormatException`.
6. **Decimals and exponents without suffix** (there is a `.` or an exponent): compute the "all zeros" flag as above. Try, in this order: create a `Float f` and a `Double d` from `str`. Return `f` if it is finite, is not zero while the digits are not all zeros, and `f.toString()` equals `d.toString()`. Otherwise, if `d` is finite and is not zero while the digits are not all zeros: build `BigDecimal b = createBigDecimal(str)`; return `d` if `b` compares equal (`compareTo == 0`) to `BigDecimal.valueOf(d)`, otherwise return `b`. If the conversions throw `NumberFormatException`, or neither returns, return `createBigDecimal(str)` (its exception propagates).

## 3. Input specification

`str`: a `String` or `null`. The helper methods `createInteger`, `createLong`, `createBigInteger`, `createFloat`, `createDouble`, `createBigDecimal` (each returns `null` for `null` input), `isDigits` and `isAllZeros` exist in the same class and may be called.

## 4. Output specification

A `Number` (`Integer`, `Long`, `BigInteger`, `Float`, `Double` or `BigDecimal`) or `null`. Examples: `"12345"` -> `Integer 12345`; `"2147483648"` -> `Long`; `"12345L"` -> `Long 12345`; `"1234.5"` -> `Float`; `"1234.5D"` -> `Double 1234.5`; `"1234.5F"` -> `Float`; `"1.1E200"` -> `Double`; `"3.4028235e+38"` -> `Float`; `"3.4028236e+38"` -> `Double`; `"1.797693134862315759e+308"` -> `BigDecimal`; `"0xFADE"` -> `Integer 64222`; `"0x80000000"` -> `Long`; `"0x7fffffffffffffff0"` -> `BigInteger`; `"017777777777"` -> `Integer`; `"037777777777"` -> `Long`; `"-0.0"`, `"+0.0"`, `"0.0"` -> `Float`; `"001.12"`, `"-001.12"`, `"+001.12"` -> `Float`; `"1234.5ff"`, `"1234.5dd"`, `"--1.1E-700F"`, `"-1.1E+0-7e00"`, `"1eE+00001"` -> `NumberFormatException`.

## 5. Edge cases and constraints

- Failures are always `NumberFormatException` (the tests check the type; the explicit messages above should be kept where given).
- Pure function; the string is not modified. Very long digit strings must be supported (BigInteger/BigDecimal results).
