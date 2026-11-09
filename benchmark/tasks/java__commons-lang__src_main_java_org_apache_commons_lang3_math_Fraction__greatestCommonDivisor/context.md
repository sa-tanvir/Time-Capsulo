# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/math/Fraction.java`
- **Enclosing scope:** `public final class Fraction extends Number implements Comparable<Fraction>`

## Imports / includes available in this file

```
import java.math.BigInteger;
import org.apache.commons.lang3.Validate;
```

## Other functions defined in the same file (signatures only; you may call them)

```
Fraction::Fraction( final int numerator , final int denominator)
Fraction::abs()
Fraction::add( final Fraction fraction)
Fraction::addAndCheck( final int x , final int y)
Fraction::addSub( final Fraction fraction , final boolean isAdd)
Fraction::compareTo( final Fraction other)
Fraction::divideBy( final Fraction fraction)
Fraction::doubleValue()
Fraction::equals( final Object obj)
Fraction::floatValue()
Fraction::getDenominator()
Fraction::getFraction( String str)
Fraction::getFraction( double value)
Fraction::getFraction( final int whole , final int numerator , final int denominator)
Fraction::getFraction( int numerator , int denominator)
Fraction::getNumerator()
Fraction::getProperNumerator()
Fraction::getProperWhole()
Fraction::getReducedFraction( int numerator , int denominator)
Fraction::hashCode()
Fraction::intValue()
Fraction::invert()
Fraction::longValue()
Fraction::mulAndCheck( final int x , final int y)
Fraction::mulPosAndCheck( final int x , final int y)
Fraction::multiplyBy( final Fraction fraction)
Fraction::negate()
Fraction::pow( final int power)
Fraction::reduce()
Fraction::subAndCheck( final int x , final int y)
Fraction::subtract( final Fraction fraction)
Fraction::toProperString()
Fraction::toString()
```

## Instance state

`greatestCommonDivisor(int, int)` is a private static method of `Fraction`; it reads no fields. It is used by `reduce()`, `getReducedFraction`, `addSub`, `multiplyBy`, `divideBy` and similar methods to reduce fractions, so the result is used as a divisor of numerators/denominators.
