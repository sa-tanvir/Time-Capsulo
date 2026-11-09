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
NumberUtils::getMantissa( final String str , final int stopPos)
NumberUtils::getMantissa( final String str)
NumberUtils::isAllZeros( final String str)
NumberUtils::isCreatable( final String str)
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

`createNumber(String)` is a public static method of `NumberUtils`; it reads no fields. Helper behaviour (all public/private static in the same class): `createInteger(String)` = `Integer.decode`, `createLong(String)` = `Long.decode` (both accept a sign, `0x`/`0X`/`#` hex and a leading-`0` octal form, `null` -> `null`); `createBigInteger(String)` handles an optional `-`, then `0x`/`0X`/`#` (hex), or a leading `0` followed by more digits (octal), else decimal; `createFloat`/`createDouble` = `Float.valueOf`/`Double.valueOf` (`null` -> `null`); `createBigDecimal(String)` throws `NumberFormatException("A blank string is not a valid number")` for blank input and otherwise uses `new BigDecimal(str)`; `isDigits(String)` is true for a non-empty all-digit string; `isAllZeros(String)` is true for `null`, and for a non-empty string of only `0` characters (false for the empty string).
