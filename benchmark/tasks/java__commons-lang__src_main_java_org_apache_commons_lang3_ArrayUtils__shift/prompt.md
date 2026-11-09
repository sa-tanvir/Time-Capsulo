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

`ArrayUtils.shift(array, startIndexInclusive, endIndexExclusive, offset)` rotates the elements of a range of a `byte[]` **in place**, cyclically, by `offset` positions towards higher indices. Elements pushed past the end of the range re-enter at its start. Elements outside the range are not touched.

## 2. Functional requirements

1. Do nothing (return normally) if `array` is `null`.
2. Do nothing if `startIndexInclusive >= array.length - 1` or `endIndexExclusive <= 0`.
3. Clamp the range: a negative `startIndexInclusive` is treated as `0`; an `endIndexExclusive` larger than `array.length` is treated as `array.length`.
4. Let `n = end - start` for the clamped range. If `n <= 1` do nothing (this includes `end <= start`).
5. Otherwise rotate the range right by `offset`: the element at index `start + i` (`0 <= i < n`) moves to index `start + ((i + offset) mod n)`, where the modulus is taken in the mathematical sense (never negative). Negative `offset` therefore rotates left, `offset` may be any `int` (including `Integer.MIN_VALUE` and `Integer.MAX_VALUE`) and an offset that is a multiple of `n` leaves the array unchanged.
6. The array is modified in place and nothing is returned. No copy of the whole range may be needed: the operation should work with constant extra space and time linear in `n` (performance is measured on arrays of millions of elements).

## 3. Input specification

`array`: `byte[]`, may be `null`. `startIndexInclusive`, `endIndexExclusive`: any `int` (may be out of bounds as described). `offset`: any `int`.

## 4. Output specification

`void`. Examples: `[1,2,3,4,5]`, `shift(1, 3, 1)` -> `[1,3,2,4,5]`; then `shift(1, 4, 2)` -> `[1,2,4,3,5]`; `[1,2,3,4]`, `shift(1, 1, 1)` -> unchanged; `[1,2,3,4]`, `shift(0, 4, 4)` and `shift(0, 4, -4)` -> unchanged; `[1,2,3,4]`, `shift(0, 4, 1)` -> `[4,1,2,3]`; `[1,2,3,4]`, `shift(0, 4, -1)` -> `[2,3,4,1]`; `[1,2,3,4,5,6]`, `shift(-3, 100, 2)` -> `[5,6,1,2,3,4]`; `null` array -> no effect.

## 5. Edge cases and constraints

- No exception is thrown for any index or offset values.
- Not thread-safe (mutates the array).

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/lang3/ArrayUtils.java`
- **Enclosing scope:** `public class ArrayUtils`

## Imports / includes available in this file

```
import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import org.apache.commons.lang3.math.NumberUtils;
import org.apache.commons.lang3.mutable.MutableInt;
```

## Other functions defined in the same file (signatures only; you may call them)

```
ArrayUtils::ArrayUtils()
ArrayUtils::add( final Object array , final int index , final Object element , final Class <?> clss)
ArrayUtils::add( final T [ ] array , final T element)
ArrayUtils::add( final T [ ] array , final int index , final T element)
ArrayUtils::add( final boolean [ ] array , final boolean element)
ArrayUtils::add( final boolean [ ] array , final int index , final boolean element)
ArrayUtils::add( final byte [ ] array , final byte element)
ArrayUtils::add( final byte [ ] array , final int index , final byte element)
ArrayUtils::add( final char [ ] array , final char element)
ArrayUtils::add( final char [ ] array , final int index , final char element)
ArrayUtils::add( final double [ ] array , final double element)
ArrayUtils::add( final double [ ] array , final int index , final double element)
ArrayUtils::add( final float [ ] array , final float element)
ArrayUtils::add( final float [ ] array , final int index , final float element)
ArrayUtils::add( final int [ ] array , final int element)
ArrayUtils::add( final int [ ] array , final int index , final int element)
ArrayUtils::add( final long [ ] array , final int index , final long element)
ArrayUtils::add( final long [ ] array , final long element)
ArrayUtils::add( final short [ ] array , final int index , final short element)
ArrayUtils::add( final short [ ] array , final short element)
ArrayUtils::addAll( final T [ ] array1 , final T ... array2)
ArrayUtils::addAll( final boolean [ ] array1 , final boolean ... array2)
ArrayUtils::addAll( final byte [ ] array1 , final byte ... array2)
ArrayUtils::addAll( final char [ ] array1 , final char ... array2)
ArrayUtils::addAll( final double [ ] array1 , final double ... array2)
ArrayUtils::addAll( final float [ ] array1 , final float ... array2)
ArrayUtils::addAll( final int [ ] array1 , final int ... array2)
ArrayUtils::addAll( final long [ ] array1 , final long ... array2)
ArrayUtils::addAll( final short [ ] array1 , final short ... array2)
ArrayUtils::clone( final T [ ] array)
ArrayUtils::clone( final boolean [ ] array)
ArrayUtils::clone( final byte [ ] array)
ArrayUtils::clone( final char [ ] array)
ArrayUtils::clone( final double [ ] array)
ArrayUtils::clone( final float [ ] array)
ArrayUtils::clone( final int [ ] array)
ArrayUtils::clone( final long [ ] array)
ArrayUtils::clone( final short [ ] array)
ArrayUtils::contains( final Object [ ] array , final Object objectToFind)
ArrayUtils::contains( final boolean [ ] array , final boolean valueToFind)
ArrayUtils::contains( final byte [ ] array , final byte valueToFind)
ArrayUtils::contains( final char [ ] array , final char valueToFind)
ArrayUtils::contains( final double [ ] array , final double valueToFind , final double tolerance)
ArrayUtils::contains( final double [ ] array , final double valueToFind)
ArrayUtils::contains( final float [ ] array , final float valueToFind)
ArrayUtils::contains( final int [ ] array , final int valueToFind)
ArrayUtils::contains( final long [ ] array , final long valueToFind)
ArrayUtils::contains( final short [ ] array , final short valueToFind)
ArrayUtils::copyArrayGrow1( final Object array , final Class <?> newArrayComponentType)
ArrayUtils::getLength( final Object array)
ArrayUtils::hashCode( final Object array)
ArrayUtils::indexOf( final Object [ ] array , final Object objectToFind , int startIndex)
ArrayUtils::indexOf( final Object [ ] array , final Object objectToFind)
ArrayUtils::indexOf( final boolean [ ] array , final boolean valueToFind , int startIndex)
ArrayUtils::indexOf( final boolean [ ] array , final boolean valueToFind)
ArrayUtils::indexOf( final byte [ ] array , final byte valueToFind , int startIndex)
ArrayUtils::indexOf( final byte [ ] array , final byte valueToFind)
ArrayUtils::indexOf( final char [ ] array , final char valueToFind , int startIndex)
ArrayUtils::indexOf( final char [ ] array , final char valueToFind)
ArrayUtils::indexOf( final double [ ] array , final double valueToFind , final double tolerance)
ArrayUtils::indexOf( final double [ ] array , final double valueToFind , int startIndex , final double tolerance)
ArrayUtils::indexOf( final double [ ] array , final double valueToFind , int startIndex)
ArrayUtils::indexOf( final double [ ] array , final double valueToFind)
ArrayUtils::indexOf( final float [ ] array , final float valueToFind , int startIndex)
ArrayUtils::indexOf( final float [ ] array , final float valueToFind)
ArrayUtils::indexOf( final int [ ] array , final int valueToFind , int startIndex)
ArrayUtils::indexOf( final int [ ] array , final int valueToFind)
ArrayUtils::indexOf( final long [ ] array , final long valueToFind , int startIndex)
ArrayUtils::indexOf( final long [ ] array , final long valueToFind)
ArrayUtils::indexOf( final short [ ] array , final short valueToFind , int startIndex)
ArrayUtils::indexOf( final short [ ] array , final short valueToFind)
ArrayUtils::insert( final int index , final T [ ] array , final T ... values)
ArrayUtils::insert( final int index , final boolean [ ] array , final boolean ... values)
ArrayUtils::insert( final int index , final byte [ ] array , final byte ... values)
ArrayUtils::insert( final int index , final char [ ] array , final char ... values)
ArrayUtils::insert( final int index , final double [ ] array , final double ... values)
ArrayUtils::insert( final int index , final float [ ] array , final float ... values)
ArrayUtils::insert( final int index , final int [ ] array , final int ... values)
ArrayUtils::insert( final int index , final long [ ] array , final long ... values)
ArrayUtils::insert( final int index , final short [ ] array , final short ... values)
ArrayUtils::isArrayIndexValid( T [ ] array , int index)
ArrayUtils::isEmpty( final Object [ ] array)
ArrayUtils::isEmpty( final boolean [ ] array)
ArrayUtils::isEmpty( final byte [ ] array)
ArrayUtils::isEmpty( final char [ ] array)
ArrayUtils::isEmpty( final double [ ] array)
ArrayUtils::isEmpty( final float [ ] array)
ArrayUtils::isEmpty( final int [ ] array)
ArrayUtils::isEmpty( final long [ ] array)
ArrayUtils::isEmpty( final short [ ] array)
ArrayUtils::isEquals( final Object array1 , final Object array2)
ArrayUtils::isNotEmpty( final T [ ] array)
ArrayUtils::isNotEmpty( final boolean [ ] array)
ArrayUtils::isNotEmpty( final byte [ ] array)
ArrayUtils::isNotEmpty( final char [ ] array)
ArrayUtils::isNotEmpty( final double [ ] array)
ArrayUtils::isNotEmpty( final float [ ] array)
ArrayUtils::isNotEmpty( final int [ ] array)
ArrayUtils::isNotEmpty( final long [ ] array)
ArrayUtils::isNotEmpty( final short [ ] array)
ArrayUtils::isSameLength( final Object [ ] array1 , final Object [ ] array2)
ArrayUtils::isSameLength( final boolean [ ] array1 , final boolean [ ] array2)
ArrayUtils::isSameLength( final byte [ ] array1 , final byte [ ] array2)
ArrayUtils::isSameLength( final char [ ] array1 , final char [ ] array2)
ArrayUtils::isSameLength( final double [ ] array1 , final double [ ] array2)
ArrayUtils::isSameLength( final float [ ] array1 , final float [ ] array2)
ArrayUtils::isSameLength( final int [ ] array1 , final int [ ] array2)
ArrayUtils::isSameLength( final long [ ] array1 , final long [ ] array2)
ArrayUtils::isSameLength( final short [ ] array1 , final short [ ] array2)
ArrayUtils::isSameType( final Object array1 , final Object array2)
ArrayUtils::isSorted( final T [ ] array , final Comparator<T> comparator)
ArrayUtils::isSorted( final T [ ] array)
ArrayUtils::isSorted( final boolean [ ] array)
ArrayUtils::isSorted( final byte [ ] array)
ArrayUtils::isSorted( final char [ ] array)
ArrayUtils::isSorted( final double [ ] array)
ArrayUtils::isSorted( final float [ ] array)
ArrayUtils::isSorted( final int [ ] array)
ArrayUtils::isSorted( final long [ ] array)
ArrayUtils::isSorted( final short [ ] array)
ArrayUtils::lastIndexOf( final Object [ ] array , final Object objectToFind , int startIndex)
ArrayUtils::lastIndexOf( final Object [ ] array , final Object objectToFind)
ArrayUtils::lastIndexOf( final boolean [ ] array , final boolean valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final boolean [ ] array , final boolean valueToFind)
ArrayUtils::lastIndexOf( final byte [ ] array , final byte valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final byte [ ] array , final byte valueToFind)
ArrayUtils::lastIndexOf( final char [ ] array , final char valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final char [ ] array , final char valueToFind)
ArrayUtils::lastIndexOf( final double [ ] array , final double valueToFind , final double tolerance)
ArrayUtils::lastIndexOf( final double [ ] array , final double valueToFind , int startIndex , final double tolerance)
ArrayUtils::lastIndexOf( final double [ ] array , final double valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final double [ ] array , final double valueToFind)
ArrayUtils::lastIndexOf( final float [ ] array , final float valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final float [ ] array , final float valueToFind)
ArrayUtils::lastIndexOf( final int [ ] array , final int valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final int [ ] array , final int valueToFind)
ArrayUtils::lastIndexOf( final long [ ] array , final long valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final long [ ] array , final long valueToFind)
ArrayUtils::lastIndexOf( final short [ ] array , final short valueToFind , int startIndex)
ArrayUtils::lastIndexOf( final short [ ] array , final short valueToFind)
ArrayUtils::nullToEmpty( final Boolean [ ] array)
ArrayUtils::nullToEmpty( final Byte [ ] array)
ArrayUtils::nullToEmpty( final Character [ ] array)
ArrayUtils::nullToEmpty( final Class <?> [ ] array)
ArrayUtils::nullToEmpty( final Double [ ] array)
ArrayUtils::nullToEmpty( final Float [ ] array)
ArrayUtils::nullToEmpty( final Integer [ ] array)
ArrayUtils::nullToEmpty( final Long [ ] array)
ArrayUtils::nullToEmpty( final Object [ ] array)
ArrayUtils::nullToEmpty( final Short [ ] array)
ArrayUtils::nullToEmpty( final String [ ] array)
ArrayUtils::nullToEmpty( final T [ ] array , final Class<T[]> type)
ArrayUtils::nullToEmpty( final boolean [ ] array)
ArrayUtils::nullToEmpty( final byte [ ] array)
ArrayUtils::nullToEmpty( final char [ ] array)
ArrayUtils::nullToEmpty( final double [ ] array)
ArrayUtils::nullToEmpty( final float [ ] array)
ArrayUtils::nullToEmpty( final int [ ] array)
ArrayUtils::nullToEmpty( final long [ ] array)
ArrayUtils::nullToEmpty( final short [ ] array)
ArrayUtils::remove( final Object array , final int index)
ArrayUtils::remove( final T [ ] array , final int index)
ArrayUtils::remove( final boolean [ ] array , final int index)
ArrayUtils::remove( final byte [ ] array , final int index)
ArrayUtils::remove( final char [ ] array , final int index)
ArrayUtils::remove( final double [ ] array , final int index)
ArrayUtils::remove( final float [ ] array , final int index)
ArrayUtils::remove( final int [ ] array , final int index)
ArrayUtils::remove( final long [ ] array , final int index)
ArrayUtils::remove( final short [ ] array , final int index)
ArrayUtils::removeAll( final Object array , final BitSet indices)
ArrayUtils::removeAll( final Object array , final int ... indices)
ArrayUtils::removeAll( final T [ ] array , final int ... indices)
ArrayUtils::removeAll( final boolean [ ] array , final int ... indices)
ArrayUtils::removeAll( final byte [ ] array , final int ... indices)
ArrayUtils::removeAll( final char [ ] array , final int ... indices)
ArrayUtils::removeAll( final double [ ] array , final int ... indices)
ArrayUtils::removeAll( final float [ ] array , final int ... indices)
ArrayUtils::removeAll( final int [ ] array , final int ... indices)
ArrayUtils::removeAll( final long [ ] array , final int ... indices)
ArrayUtils::removeAll( final short [ ] array , final int ... indices)
ArrayUtils::removeAllOccurences( final T [ ] array , final T element)
ArrayUtils::removeAllOccurences( final boolean [ ] array , final boolean element)
ArrayUtils::removeAllOccurences( final byte [ ] array , final byte element)
ArrayUtils::removeAllOccurences( final char [ ] array , final char element)
ArrayUtils::removeAllOccurences( final double [ ] array , final double element)
ArrayUtils::removeAllOccurences( final float [ ] array , final float element)
ArrayUtils::removeAllOccurences( final int [ ] array , final int element)
ArrayUtils::removeAllOccurences( final long [ ] array , final long element)
ArrayUtils::removeAllOccurences( final short [ ] array , final short element)
ArrayUtils::removeElement( final T [ ] array , final Object element)
ArrayUtils::removeElement( final boolean [ ] array , final boolean element)
ArrayUtils::removeElement( final byte [ ] array , final byte element)
ArrayUtils::removeElement( final char [ ] array , final char element)
ArrayUtils::removeElement( final double [ ] array , final double element)
ArrayUtils::removeElement( final float [ ] array , final float element)
ArrayUtils::removeElement( final int [ ] array , final int element)
ArrayUtils::removeElement( final long [ ] array , final long element)
ArrayUtils::removeElement( final short [ ] array , final short element)
ArrayUtils::removeElements( final T [ ] array , final T ... values)
```

## Instance state

`shift(byte[], int, int, int)` is a public static method of `ArrayUtils`; it reads no fields. The sibling `shift(byte[] array, int offset)` shifts the whole array and delegates to it. A public static helper `swap(byte[] array, int offset1, int offset2, int len)` exists in the class: it exchanges the `len` elements starting at `offset1` with those starting at `offset2` (no-op for a null or empty array; ranges are clamped to the array bounds).

=== STUB ===
```java
public static void shift(final byte[] array, int startIndexInclusive, int endIndexExclusive, int offset) {
    // TODO: implement according to the specification
}
```
