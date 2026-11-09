# Functional specification

## 1. Component overview

`TextStringBuilder.lastIndexOf(str, startIndex)` searches the builder's content backwards for the last occurrence of `str` that starts at or before `startIndex`, and returns its start position (or `-1`). It is the `String` counterpart of `String.lastIndexOf(String, int)`, with lenient handling of bad arguments.

## 2. Functional requirements

Let `size` be the number of characters currently in the builder and `s` the content `buffer[0..size)`.

1. **Clamp the start.** If `startIndex >= size`, it is replaced by `size - 1`.
2. If `str` is `null`, or the (clamped) `startIndex` is negative, return `-1`. (This includes any search on an empty builder, because the clamped start is then `-1`, even for an empty `str`.)
3. If `str` is empty, return the (clamped) `startIndex`.
4. If `str` is longer than `size`, return `-1`.
5. If `str` has length 1, the result equals `lastIndexOf(str.charAt(0), startIndex)`.
6. Otherwise return the greatest index `i >= 0` such that the match lies entirely at or before the (clamped) `startIndex` (that is, `i + str.length() - 1 <= startIndex`) and `s[i .. i+str.length())` equals `str`. If no such `i` exists, return `-1`.

## 3. Input specification

`str`: any string or `null`. `startIndex`: any `int` (negative, in range, or beyond the size). The builder may be empty and its internal array may be larger than `size` with arbitrary leftover characters after the content.

## 4. Output specification

An `int`: the index of the last match, or `-1`. The method never throws. Examples with content `"abcabc"` (size 6): `lastIndexOf("bc", 5)` = 4; `lastIndexOf("bc", 4)` = 1 (the match at 4 would end at index 5, beyond the start); `lastIndexOf("bc", 100)` = 4; `lastIndexOf("abc", -1)` = -1; `lastIndexOf("", 3)` = 3; `lastIndexOf("", 100)` = 5; `lastIndexOf(null, 3)` = -1; `lastIndexOf("abcabcabc", 5)` = -1; `lastIndexOf("a", 5)` = 3; `lastIndexOf("x", 5)` = -1.

## 5. Edge cases and constraints

- Does not modify the builder; matches never extend beyond `size` (stale characters in the backing array must not be matched).
- Matches are case sensitive.
