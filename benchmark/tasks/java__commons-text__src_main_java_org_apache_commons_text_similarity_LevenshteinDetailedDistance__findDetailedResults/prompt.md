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

`LevenshteinDetailedDistance.findDetailedResults(left, right, matrix, swapped)` takes a completed Levenshtein cost table for two character sequences and recovers how many insertions, deletions and substitutions make up one optimal edit path from `left` to `right`. It returns a `LevenshteinResults` with the total distance and the three counts.

## 2. Functional requirements

Walk the table from its bottom-right corner (row `right.length()`, column `left.length()`) towards the top-left corner, counting the operations on the way. At every position, with `r` the current row and `c` the current column:

1. The neighbouring cells are: left = `matrix[r][c-1]`, top = `matrix[r-1][c]`, diagonal = `matrix[r-1][c-1]`. A neighbour that lies outside the table (the left neighbour when `c == 0`, the top neighbour when `r == 0`, the diagonal when `r == 0` or `c == 0`) counts as the value `-1`.
2. If all three neighbours are `-1`, stop. The walk also stops when `r` or `c` would become negative.
3. If `c > 0`, `r > 0` and `left.charAt(c-1) == right.charAt(r-1)`, the characters match: move diagonally (`r--`, `c--`) without counting anything.
4. Otherwise let `data = matrix[r][c]` and decide the operation:
   - **Step left (consumes a column)** if `data - 1` equals the left neighbour **and** `data` is not greater than the diagonal neighbour **and** not greater than the top neighbour; or if both the diagonal and the top neighbour are outside the table (`-1`). Then `c--`. This counts as a deletion if `swapped` is false, otherwise as an insertion.
   - **Step up (consumes a row)** otherwise, if `data - 1` equals the top neighbour **and** `data` is not greater than the diagonal neighbour **and** not greater than the left neighbour; or if both the diagonal and the left neighbour are outside the table. Then `r--`. This counts as an insertion if `swapped` is false, otherwise as a deletion.
   - **Substitution** if neither of the two previous cases applied: count one substitution and move diagonally (`r--`, `c--`).
   The "step left" test is evaluated before the "step up" test.
5. After the walk, return `new LevenshteinResults(insertions + deletions + substitutions, insertions, deletions, substitutions)`.

## 3. Input specification

- `left`, `right`: non-empty `CharSequence`s, `left.length() <= right.length()`.
- `matrix`: a valid cost table as described in the context, dimensions `(right.length()+1) x (left.length()+1)`.
- `swapped`: any boolean.
No `null` handling is required.

## 4. Output specification

A new `LevenshteinResults` (distance, insert count, delete count, substitute count). The distance field is always the sum of the three counts. The method does not modify its arguments.

Examples: with `left = "kitten"`, `right = "sitting"`, a correct cost table and `swapped = false` the result is distance 3 with 1 insertion, 0 deletions and 2 substitutions. With `left = "a"`, `right = "abc"` (`swapped = false`) it is distance 2, 2 insertions. With the same table and `swapped = true` the 2 operations are deletions.

## 5. Edge cases and constraints

- Identical sequences give `0, 0, 0, 0`.
- When the sequences have different lengths the remaining characters of `right` after the walk reaches column 0 are counted as insertions (deletions if `swapped`), following the rules above.
- Ties between equally good paths must be resolved exactly with the order of checks in section 2, because the individual counts (not only the distance) are compared by callers.
- Pure and thread-safe.

=== CONTEXT ===
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

=== STUB ===
```java
private static LevenshteinResults findDetailedResults(final CharSequence left,
                                                      final CharSequence right,
                                                      final int[][] matrix,
                                                      final boolean swapped) {
    // TODO: implement according to the specification
}
```
