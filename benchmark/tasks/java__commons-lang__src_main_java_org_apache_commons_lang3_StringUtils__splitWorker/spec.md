# Functional specification

## 1. Component overview

`StringUtils.splitWorker(str, separatorChars, max, preserveAllTokens)` is the private worker behind the `split(...)` and `splitPreserveAllTokens(...)` families. It splits a string into an array of tokens at any of a set of separator characters, with an optional cap on the number of tokens.

## 2. Functional requirements

1. If `str` is `null`, return `null`. If `str` is the empty string, return an empty array (for all other parameters).
2. Separators: if `separatorChars` is `null`, a separator is any character for which `Character.isWhitespace(char)` is true. Otherwise a separator is any character contained in `separatorChars`; each `char` is considered on its own, so `separatorChars` is a set of single characters, not a delimiter string. An empty `separatorChars` string contains no separators, so the whole `str` is a single token.
3. Tokens, when `preserveAllTokens` is `false`: the maximal runs of non-separator characters, in order. Adjacent separators act as one; leading and trailing separators produce nothing. A `str` made only of separators yields an empty array.
4. Tokens, when `preserveAllTokens` is `true`: every separator ends a token, so adjacent separators produce empty-string tokens between them, a separator at the very start produces a leading empty token, and a separator at the very end produces a trailing empty token. A `str` of `k` separators only yields `k + 1` empty strings. A non-empty `str` without any separator yields exactly one token (itself).
5. `max` limits the number of returned elements: `max <= 0` means no limit. If `max > 0` and the string has more than `max` tokens by the rules above, the result has exactly `max` elements, and the last element is the entire remainder of `str` starting at the beginning of the `max`-th token and running to the end of `str`, including any separators that follow (not trimmed and not split). If the number of tokens is at most `max`, nothing special happens, except that when the `max`-th token is followed by a separator, then that last element also extends to the end of the string (e.g. `"a b "`, `" "`, `2`, `false` -> `["a", "b "]`).
6. The returned array is new; `str` is not modified.

## 3. Input specification

`str`: `String` or `null`. `separatorChars`: `String` or `null` (whitespace). `max`: any `int`. `preserveAllTokens`: `boolean`.

## 4. Output specification

A `String[]` (or `null`). Examples:
- `("a b  c", null, 0, false)` -> `["a","b","c"]`
- `("a b  c", null, 0, true)` -> `["a","b","","c"]`
- `(" a ", " ", 0, true)` -> `["","a",""]`
- `(" a ", " ", 0, false)` -> `["a"]`
- `("a,b;c d", ",; ", 0, false)` -> `["a","b","c","d"]`
- `("a:b:c", ":", 2, false)` -> `["a","b:c"]`
- `("a:b:c:", ":", 3, true)` -> `["a","b","c:"]`; with max 4 -> `["a","b","c",""]`
- `("a b  c d", " ", 3, false)` -> `["a","b","c d"]`
- `("abc", "", 0, false)` -> `["abc"]`
- `("", ",", 0, true)` -> `[]`

## 5. Edge cases and constraints

- Work must be linear in the length of `str`.
- Pure function, thread-safe.
