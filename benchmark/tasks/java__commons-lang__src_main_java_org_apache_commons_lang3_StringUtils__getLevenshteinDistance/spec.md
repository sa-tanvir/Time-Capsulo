# Functional specification

## 1. Component overview

`StringUtils.getLevenshteinDistance(s, t, threshold)` returns the Levenshtein edit distance between two character sequences if it is at most `threshold`, and `-1` otherwise. Comparison is per `char`, case sensitive, with unit cost for insertion, deletion and substitution.

## 2. Functional requirements

1. If `s` or `t` is `null`, throw `IllegalArgumentException` with the message `Strings must not be null`.
2. If `threshold < 0`, throw `IllegalArgumentException` with the message `Threshold must not be negative`. The null check comes first (both checks happen before any other work, also for empty strings).
3. If one sequence is empty, return the length of the other if that length is `<= threshold`, else `-1`. Two empty sequences give `0`.
4. Otherwise compute the minimal number of single-character insertions, deletions and substitutions needed to turn `s` into `t`. Return it if it is `<= threshold`; return `-1` if it is greater. In particular, return `-1` immediately when the length difference alone exceeds the threshold.
5. The result must be correct for every threshold, including very large ones (up to `Integer.MAX_VALUE`) without integer overflow. For a threshold much smaller than the sequence lengths the work should be proportional to the threshold times the longer length rather than the full product of the lengths (performance is measured).

## 3. Input specification

`s`, `t`: `CharSequence` values (empty allowed, `null` rejected as above). `threshold`: any `int`.

## 4. Output specification

An `int`: the distance (0 to max(len)) or `-1`. Examples: `("elephant","hippo", 7)` -> 7; `("elephant","hippo", 6)` -> -1; `("frog","fog",1)` -> 1; `("","",0)` -> 0; `("aaapppp","",7)` -> 7; `("aaapppp","",6)` -> -1; `("aaa","bbb",3)` -> 3; `("aaa","bbb",2)` -> -1; `("12345","1234567",1)` -> -1; `("aaaaaa","b",10)` -> 6; `("a","b",0)` -> -1.

## 5. Edge cases and constraints

- The distance is symmetric in `s` and `t`.
- Equal sequences give `0` for every non-negative threshold.
- Inputs are not modified; the method is pure and thread-safe.
- Exception types and messages above are tested.
