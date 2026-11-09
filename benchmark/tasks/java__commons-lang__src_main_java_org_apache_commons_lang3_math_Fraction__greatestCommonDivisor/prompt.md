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

`Fraction.greatestCommonDivisor(u, v)` returns the greatest common divisor of two `int` values as a non-negative `int`. It must work for the entire `int` range, including `Integer.MIN_VALUE`, whose absolute value does not fit in an `int`.

## 2. Functional requirements

1. If either `u` or `v` is `0`:
   - if either argument is `Integer.MIN_VALUE`, throw `ArithmeticException` with the message `overflow: gcd is 2^31` (the true gcd, 2^31, does not fit);
   - otherwise return `|u| + |v|` (so `gcd(0, 0) = 0` and `gcd(0, x) = |x|`).
2. Otherwise, if either `|u|` or `|v|` equals `1`, return `1`.
3. Otherwise return the mathematical gcd of `|u|` and `|v|`, where the sign of the arguments is ignored (`gcd(-12, 18) = 6`, `gcd(12, -18) = 6`, `gcd(-12, -18) = 6`). The result is always positive in this case.
4. If the true gcd is `2^31` (which happens only when both arguments are `Integer.MIN_VALUE`), throw `ArithmeticException` with the message `overflow: gcd is 2^31`. Every other pair with a nonzero argument has a gcd that fits in an `int`; for example `gcd(Integer.MIN_VALUE, 2^30) = 2^30` and `gcd(Integer.MIN_VALUE, 6) = 2`.
5. The computation must never overflow or produce a wrong result for any `int` pair. Performance is measured: the method is called many times on large operands.

## 3. Input specification

`u`, `v`: any `int` values.

## 4. Output specification

A non-negative `int` (zero only for `(0, 0)`). Examples: `(0, 0)` -> 0; `(0, -5)` -> 5; `(-5, 0)` -> 5; `(1, 99)` -> 1; `(-1, 99)` -> 1; `(12, 18)` -> 6; `(-12, 18)` -> 6; `(17, 5)` -> 1; `(1024, 96)` -> 32; `(Integer.MIN_VALUE, 0)` -> exception; `(Integer.MIN_VALUE, Integer.MIN_VALUE)` -> exception; `(Integer.MIN_VALUE, 1)` -> 1; `(Integer.MAX_VALUE, Integer.MIN_VALUE)` -> 1.

## 5. Edge cases and constraints

- Symmetric in `u` and `v`.
- Pure function, thread-safe; no argument validation other than the overflow cases above.
- Exception type and message are tested.

=== CONTEXT ===
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

=== STUB ===
```java
private static int greatestCommonDivisor(int u, int v) {
    // TODO: implement according to the specification
}
```
