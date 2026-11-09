# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/similarity/LevenshteinDetailedDistance.java`
- **Enclosing scope:** `public class LevenshteinDetailedDistance implements EditDistance<LevenshteinResults>`

## Imports / includes available in this file

```
import java.util.Arrays;
```

## Other functions defined in the same file (signatures only; you may call them)

```
LevenshteinDetailedDistance::LevenshteinDetailedDistance( final Integer threshold)
LevenshteinDetailedDistance::LevenshteinDetailedDistance()
LevenshteinDetailedDistance::apply( final CharSequence left , final CharSequence right)
LevenshteinDetailedDistance::findDetailedResults( final CharSequence left , final CharSequence right , final int [ ] [ ] matrix , final boolean swapped)
LevenshteinDetailedDistance::getDefaultInstance()
LevenshteinDetailedDistance::getThreshold()
LevenshteinDetailedDistance::unlimitedCompare( CharSequence left , CharSequence right)
```

## Instance state

`limitedCompare` is a private static method and reads no fields. It is reached from the instance method `apply(CharSequence, CharSequence)` when the instance was built with a non-null threshold (the threshold is the instance's `Integer threshold` field, passed in as the third parameter).

- `LevenshteinResults(Integer distance, Integer insertCount, Integer deleteCount, Integer substituteCount)` (same package) is the result type; getters `getDistance()`, `getInsertCount()`, `getDeleteCount()`, `getSubstituteCount()`.
- The sibling `private static LevenshteinResults findDetailedResults(CharSequence left, CharSequence right, int[][] matrix, boolean swapped)` back-traces a cost table into the three operation counts: `left` must be the shorter sequence, `matrix` has `right.length()+1` rows and `left.length()+1` columns (`matrix[r][c]` is the cost of the first `c` characters of `left` versus the first `r` characters of `right`), and `swapped` tells it whether the caller exchanged the original arguments. You may call it.
