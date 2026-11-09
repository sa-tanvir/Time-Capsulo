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
LevenshteinDetailedDistance::getDefaultInstance()
LevenshteinDetailedDistance::getThreshold()
LevenshteinDetailedDistance::limitedCompare( CharSequence left , CharSequence right , final int threshold)
LevenshteinDetailedDistance::unlimitedCompare( CharSequence left , CharSequence right)
```

## Instance state

`findDetailedResults` is a private static method; it reads no fields. Its inputs:

- `left`, `right` (`CharSequence`): the two sequences, **already ordered** by the caller so that `left` is the shorter one (or equal length). Both are non-empty.
- `matrix` (`int[][]`): the full Levenshtein cost table with `right.length() + 1` rows and `left.length() + 1` columns. `matrix[r][c]` is the edit distance between the first `c` characters of `left` and the first `r` characters of `right`. Row 0 holds `0, 1, 2, ...` and column 0 holds `0, 1, 2, ...`.
- `swapped` (`boolean`): true if the caller exchanged the original arguments to obtain this order (so a step that consumes a character of the shorter string only is, in terms of the original arguments, an insertion rather than a deletion).

Result type `LevenshteinResults` (same package) has the public constructor `LevenshteinResults(Integer distance, Integer insertCount, Integer deleteCount, Integer substituteCount)`.
