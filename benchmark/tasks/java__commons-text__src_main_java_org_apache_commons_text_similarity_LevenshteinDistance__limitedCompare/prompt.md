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

`LevenshteinDistance.limitedCompare(left, right, threshold)` returns the Levenshtein edit distance between two character sequences if it is at most `threshold`, and `-1` otherwise. It is used by `LevenshteinDistance.apply` when a threshold was configured. Comparison is per `char`, case sensitive, with unit cost for insertion, deletion and substitution.

## 2. Functional requirements

1. If `left` or `right` is `null`, throw `IllegalArgumentException` with the message `CharSequences must not be null`.
2. If `threshold < 0`, throw `IllegalArgumentException` with the message `Threshold must not be negative`. The null check comes first.
3. If `left` is empty, return `right.length()` if that is `<= threshold`, else `-1`. If `right` is empty, return `left.length()` if `<= threshold`, else `-1`. (Two empty sequences give `0`.)
4. Otherwise compute the minimal number of single-character insertions, deletions and substitutions needed to turn `left` into `right`. Return it if it is `<= threshold`; return `-1` if it is greater. In particular, return `-1` immediately when the length difference alone exceeds the threshold.
5. The result must be correct for every threshold, including very large ones (up to `Integer.MAX_VALUE`) without integer overflow. For a threshold much smaller than the sequence lengths the work should be proportional to the threshold times the longer length rather than the full product of the lengths (performance is measured).

## 3. Input specification

`left`, `right`: `CharSequence` values (empty allowed). `threshold`: any `int`.

## 4. Output specification

An `int`: the distance (0 to max(len)) or `-1`. Examples: `("elephant","hippo", 7)` -> 7; `("elephant","hippo", 6)` -> -1; `("hello","hallo", 1)` -> 1; `("","", 0)` -> 0; `("abc","", 2)` -> -1; `("kitten","sitting", 3)` -> 3; `("kitten","sitting", 2)` -> -1; `("a","b",0)` -> -1.

## 5. Edge cases and constraints

- The distance is symmetric in `left` and `right`.
- Equal sequences give `0` for every non-negative threshold.
- Inputs are not modified; the method is pure and thread-safe.
- Exception types and messages above are tested.

=== CONTEXT ===
# Context for the function to implement

- **Language:** java
- **File:** `src/main/java/org/apache/commons/text/similarity/LevenshteinDistance.java`
- **Enclosing scope:** `public class LevenshteinDistance implements EditDistance<Integer>`

## Imports / includes available in this file

```
import java.util.Arrays;
```

## Other functions defined in the same file (signatures only; you may call them)

```
LevenshteinDistance::LevenshteinDistance( final Integer threshold)
LevenshteinDistance::LevenshteinDistance()
LevenshteinDistance::apply( final CharSequence left , final CharSequence right)
LevenshteinDistance::getDefaultInstance()
LevenshteinDistance::getThreshold()
LevenshteinDistance::unlimitedCompare( CharSequence left , CharSequence right)
```

## Instance state

`limitedCompare` is a private static method and reads no fields. It is called from the instance method `apply(CharSequence, CharSequence)` when the instance was built with a non-null threshold (the `Integer threshold` field, passed here as the third parameter). `unlimitedCompare(CharSequence, CharSequence)` is the sibling used when no threshold is set.

=== STUB ===
```java
private static int limitedCompare(CharSequence left, CharSequence right, final int threshold) {
    // TODO: implement according to the specification
}
```
