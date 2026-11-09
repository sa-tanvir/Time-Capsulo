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
