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

`LevenshteinDetailedDistance.limitedCompare(left, right, threshold)` computes the Levenshtein edit distance between two character sequences together with the number of insertions, deletions and substitutions of an optimal edit path, but only if the distance does not exceed `threshold`. If it does, it reports failure with distance `-1`. Distance comparisons are case sensitive and per `char`.

## 2. Functional requirements

1. If `left` or `right` is `null`, throw `IllegalArgumentException` with the message `CharSequences must not be null`.
2. If `threshold < 0`, throw `IllegalArgumentException` with the message `Threshold must not be negative`. (The null check comes first.)
3. Unit costs: insertion, deletion and substitution each cost 1; equal characters cost 0. Let `n = left.length()`, `m = right.length()`.
4. If `left` is empty the result is distance `m` with `m` insertions (0 deletions, 0 substitutions) when `m <= threshold`; if `right` is empty the result is distance `n` with `n` deletions when `n <= threshold`. If that distance exceeds the threshold the result is distance `-1` with all counts 0. (Both empty: all zero, as `0 <= threshold`.)
5. Otherwise, if the real edit distance is `<= threshold`, return `LevenshteinResults(distance, insertCount, deleteCount, substituteCount)` where the counts add up to the distance. Insertions are characters that must be added to `left` to obtain `right`; deletions are characters of `left` that must be removed.
6. If the real distance is greater than `threshold`, return `LevenshteinResults(-1, 0, 0, 0)`. This includes the case where the length difference alone exceeds the threshold.
7. Only the distance is guaranteed to be the true minimum. The split into insert/delete/substitute counts follows the reference behaviour, in which the work is done on the shorter sequence first (the sequences are exchanged if `left` is longer, which swaps the meaning of insert and delete in the result) and the counts are recovered from a cost table in which **only the band of cells within `threshold` of the main diagonal is computed**; every other interior cell keeps the value 0 (the first row and first column hold `0,1,2,...`). The counts are then read off this table by `findDetailedResults` (see context), called as `findDetailedResults(left, right, matrix, swapped)` with the (possibly exchanged) sequences. A solution must reproduce exactly these counts, including for pairs whose optimal path is not unique.

## 3. Input specification

`left`, `right`: any `CharSequence` (including empty) or `null` (error). `threshold`: any `int`; negative is an error.

## 4. Output specification

A new `LevenshteinResults`. Examples: `("kitten","sitting", 3)` gives distance 3 (1 insert, 0 deletes, 2 substitutes); `("kitten","sitting", 2)` gives `(-1,0,0,0)`; `("", "abc", 3)` gives `(3,3,0,0)`; `("abc","", 3)` gives `(3,0,3,0)`; `("abc","abc",0)` gives `(0,0,0,0)`.

## 5. Edge cases and constraints

- Equal sequences always give `(0,0,0,0)` for any non-negative threshold.
- A very large threshold (e.g. `Integer.MAX_VALUE`) must not overflow and must behave like an unbounded comparison.
- Arguments are not modified. The method is pure and thread-safe.
- When the distance is within the threshold, the stored distance equals the sum of the three counts.

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
LevenshteinDetailedDistance::findDetailedResults( final CharSequence left , final CharSequence right , final int [ ] [ ] matrix , final boolean swapped)
LevenshteinDetailedDistance::getDefaultInstance()
LevenshteinDetailedDistance::getThreshold()
LevenshteinDetailedDistance::unlimitedCompare( CharSequence left , CharSequence right)
```

## Instance state

`limitedCompare` is a private static method and reads no fields. It is reached from the instance method `apply(CharSequence, CharSequence)` when the instance was built with a non-null threshold (the threshold is the instance's `Integer threshold` field, passed in as the third parameter).

- `LevenshteinResults(Integer distance, Integer insertCount, Integer deleteCount, Integer substituteCount)` (same package) is the result type; getters `getDistance()`, `getInsertCount()`, `getDeleteCount()`, `getSubstituteCount()`.
- The sibling `private static LevenshteinResults findDetailedResults(CharSequence left, CharSequence right, int[][] matrix, boolean swapped)` back-traces a cost table into the three operation counts: `left` must be the shorter sequence, `matrix` has `right.length()+1` rows and `left.length()+1` columns (`matrix[r][c]` is the cost of the first `c` characters of `left` versus the first `r` characters of `right`), and `swapped` tells it whether the caller exchanged the original arguments. You may call it.

=== STUB ===
```java
private static LevenshteinResults limitedCompare(CharSequence left,
                                                 CharSequence right,
                                                 final int threshold) {
    // TODO: implement according to the specification
}
```
