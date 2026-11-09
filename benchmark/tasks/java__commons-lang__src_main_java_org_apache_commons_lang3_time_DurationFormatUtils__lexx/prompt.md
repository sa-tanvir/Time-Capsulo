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

`DurationFormatUtils.lexx(format)` splits a duration format pattern (such as `"HH:mm:ss.SSS"` or `"'P'yyyy'Y'M'M'd'DT'H'H'm'M's.SSS'S'"`) into an array of `Token`s: runs of pattern letters and literal text.

## 2. Functional requirements

A `Token` has a value and a count: `new Token(Object value)` has count `1`, `Token(value, count)`, `getValue()`, `getCount()`, `increment()` (count + 1). The value of a pattern-letter token is one of the shared constants `y`, `M`, `d`, `H`, `m`, `s`, `S` (static `Object` constants of `DurationFormatUtils`, compared by identity); the value of a literal token is a `StringBuilder` holding the literal text (count 1).

Scan `format` from left to right, keeping three pieces of state: whether we are inside a quoted literal, the *current literal buffer* (a `StringBuilder` which is also the value of the last literal token in the list, or none), and the *previous letter token* (the most recently created letter token, or none). For each character `ch`:

1. If inside a quoted literal and `ch` is not `'`: append `ch` to the current literal text (no letter is interpreted) and continue.
2. If `ch` is `'`:
   - if inside a quoted literal: the literal ends (there is no current literal buffer afterwards);
   - otherwise: a new, empty literal token is appended to the list and becomes the current literal buffer, and we are now inside a quoted literal. (So `''` produces an empty literal token, and `'a''b'` produces two literal tokens `a` and `b`; there is no quote escaping.)
3. If `ch` is one of the pattern letters `y`, `M`, `d`, `H`, `m`, `s`, `S` (outside a quoted literal): if the previous letter token exists and has the same value, increment its count (even if other tokens, such as literals, were added after it; the count of the earlier token is increased and nothing is appended). Otherwise append a new letter token with count 1, which becomes the previous letter token. In both cases there is no current literal buffer afterwards.
4. Any other character outside a quoted literal: append it to the current literal buffer; if there is none, first append a new literal token to the list and make it the current buffer.

At the end, if still inside a quoted literal, throw `IllegalArgumentException` with the message `Unmatched quote in format: <format>`. Otherwise return the tokens in the order they were appended to the list, as a `Token[]`.

## 3. Input specification

`format`: a non-null `String` (possibly empty).

## 4. Output specification

A `Token[]`. Examples (`L"..."` is a literal token, `y*4` a letter token with count 4):
- `"yMdHmsS"` -> `y*1, M*1, d*1, H*1, m*1, s*1, S*1`
- `"HH:mm:ss.SSS"` -> `H*2, L":", m*2, L":", s*2, L".", S*3`
- `"'P'yyyy'Y'M'M'd'DT'H'H'm'M's.SSS'S'"` -> `L"P", y*4, L"Y", M*1, L"M", d*1, L"DT", H*1, L"H", m*1, L"M", s*1, L".", S*3, L"S"`
- `"d 'days'"` -> `d*1, L" ", L"days"`
- `"''"` -> `L""`; `"a''b"` -> `L"a", L"", L"b"`
- `"yy'x'y"` -> `y*3, L"x"`
- `""` -> empty array
- `"'abc"` -> `IllegalArgumentException`

## 5. Edge cases and constraints

- Linear time in the length of `format`.
- Characters that are neither quotes nor pattern letters (including `Y`, `D`, `T`, spaces and punctuation) are literal text.
- Pure function; thread-safe.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/time/DurationFormatUtils.java`
- **Enclosing scope:** `public class DurationFormatUtils`

## Imports / includes available in this file

```
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.TimeZone;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.Validate;
```

## Other functions defined in the same file (signatures only; you may call them)

```
DurationFormatUtils::DurationFormatUtils()
DurationFormatUtils::Token::Token( final Object value , final int count)
DurationFormatUtils::Token::Token( final Object value)
DurationFormatUtils::Token::containsTokenWithValue( final Token [ ] tokens , final Object value)
DurationFormatUtils::Token::equals( final Object obj2)
DurationFormatUtils::Token::getCount()
DurationFormatUtils::Token::getValue()
DurationFormatUtils::Token::hashCode()
DurationFormatUtils::Token::increment()
DurationFormatUtils::Token::toString()
DurationFormatUtils::format( final Token [ ] tokens , final long years , final long months , final long days , final long hours , final long minutes , final long seconds , final long milliseconds , final boolean padWithZeros)
DurationFormatUtils::formatDuration( final long durationMillis , final String format , final boolean padWithZeros)
DurationFormatUtils::formatDuration( final long durationMillis , final String format)
DurationFormatUtils::formatDurationHMS( final long durationMillis)
DurationFormatUtils::formatDurationISO( final long durationMillis)
DurationFormatUtils::formatDurationWords( final long durationMillis , final boolean suppressLeadingZeroElements , final boolean suppressTrailingZeroElements)
DurationFormatUtils::formatPeriod( final long startMillis , final long endMillis , final String format , final boolean padWithZeros , final TimeZone timezone)
DurationFormatUtils::formatPeriod( final long startMillis , final long endMillis , final String format)
DurationFormatUtils::formatPeriodISO( final long startMillis , final long endMillis)
DurationFormatUtils::paddedValue( final long value , final boolean padWithZeros , final int count)
```

## Instance state

`lexx(String)` is a package-private static method of `DurationFormatUtils`; it reads only the constants below. `DurationFormatUtils` constants: `static final Object y = "y"`, `M = "M"`, `d = "d"`, `H = "H"`, `m = "m"`, `s = "s"`, `S = "S"` (pattern-letter token values; tokens compare them with `==`). Nested class `static class Token` (package-private) with a private final `Object value`, a private `int count`, constructors `Token(Object value)` (count 1) and `Token(Object value, int count)`, methods `increment()`, `getCount()`, `getValue()`, `equals`, `hashCode`, `toString()` and `static boolean containsTokenWithValue(Token[], Object)`. `lexx` is used by `formatDuration`, `formatPeriod` and the other formatting methods.

=== STUB ===
```java
static Token[] lexx(final String format) {
    // TODO: implement according to the specification
}
```
