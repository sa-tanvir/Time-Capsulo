# Functional specification

## 1. Component overview

`StringUtils.replaceEach(text, searchList, replacementList, repeat, timeToLive)` is the private worker behind the public `replaceEach` and `replaceEachRepeatedly`. It replaces many search strings in `text` in a single left-to-right pass, optionally repeating the whole pass until the text stops changing.

## 2. Functional requirements

1. Return `text` unchanged (the same value, which may be `null`) when `text` is `null` or empty, or when `searchList` or `replacementList` is `null` or has length 0. These checks come first, before any other check.
2. If `timeToLive < 0`, throw `IllegalStateException` with the message `Aborting to protect against StackOverflowError - output of one loop is the input of another`.
3. If both arrays are non-empty but their lengths differ, throw `IllegalArgumentException` with the message `Search and Replace array lengths don't match: <searchLength> vs <replacementLength>` (for example `1 vs 2`).
4. One pass: scan `text` from the left. At each step find, among all search strings still present at or after the current position, the one with the **smallest match index**; if several match at that same index, the one with the **lowest index in `searchList`** wins. Copy the text before the match, append the corresponding replacement, and continue scanning right after the matched search string. Replacement text is never rescanned within the same pass, and matches never overlap.
5. A search entry is ignored (never matches) if the search string is `null` or empty, or if its replacement is `null`. A replacement may be the empty string (deletes the match).
6. If no search string occurs in `text`, return `text` unchanged.
7. If `repeat` is `false`, return the result of the single pass. If `repeat` is `true`, and the pass replaced at least one match, repeat the whole procedure (rules 1 to 7) on the result with `timeToLive - 1` and the same arrays, and return that outcome. A round that finds no match returns its input. Consequently, a round that replaced something while `timeToLive` is `0` leads to the `IllegalStateException` of rule 2 (the recursive call has `timeToLive == -1`), unless the result is empty (rule 1 applies first).
8. Inputs are not modified.

## 3. Input specification

`text`: `String`, may be `null` or empty. `searchList`, `replacementList`: `String[]`, either may be `null` or empty, elements may be `null` or empty. `repeat`: `boolean`. `timeToLive`: `int` (the public callers pass `0` for the non-repeating variant and `searchList.length` for the repeating one).

## 4. Output specification

A `String` (or `null` only when `text` is `null`). Examples:
- `("aba", ["a"], [""], false, 0)` -> `"b"`
- `("abcde", ["ab","d"], ["w","t"], false, 0)` -> `"wcte"`
- `("abcde", ["ab","d"], ["d","t"], false, 0)` -> `"dcte"`
- `("abc", ["a","b"], ["b","c"], false, 0)` -> `"bcc"`
- `("abc", ["a","b"], ["b","c"], true, 2)` -> `"ccc"`
- `("abcde", ["ab","d"], ["d","t"], true, 2)` -> `"tcte"`
- `("abcde", ["ab","d"], ["d","ab"], true, 2)` -> `IllegalStateException` (the output of one round is the input of the next forever)
- `("aba", ["a","b"], ["c", null], false, 0)` -> `"cbc"`
- `("aba", [null], ["a"], false, 0)` -> `"aba"`
- `("abba", ["a"], ["b","a"], false, 0)` -> `IllegalArgumentException` (`1 vs 2`)

## 5. Edge cases and constraints

- A `null`/empty `text` returns before the `timeToLive` and length checks; a negative `timeToLive` with a non-null non-empty text and non-empty arrays throws even if nothing would match.
- Performance matters: the pass should be linear in the text length times the number of search strings, without building the result through repeated string concatenation.
- Pure function, thread-safe.
