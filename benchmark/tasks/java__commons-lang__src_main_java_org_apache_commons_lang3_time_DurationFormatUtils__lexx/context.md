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
