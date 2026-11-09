# Functional specification: `unique(begin, end)`

## 1. Component overview

Part of pugixml's XPath engine (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). pugixml does not use
`<algorithm>`; this function template is its own in-place "remove consecutive duplicates" step, equivalent to
`std::unique` without a predicate. It is applied to node lists that have just been sorted into document order, so that
nodes selected more than once (for example by `a | a`, or by paths reaching the same node twice) appear only once in a node set.

## 2. Functional requirements

1. Compact the range `[begin, end)` in place: scan it from the front and keep an element only if it is **not equal**
   (`!=`) to the most recently *kept* element; the very first element is always kept. Equality is tested with the element
   type's `operator!=` (or `==`), always between a candidate and the last kept element.
2. The kept elements stay in their original relative order and occupy the front of the range contiguously:
   position 0 is the first element, position 1 is the next kept element, and so on.
3. Return an iterator one past the last kept element. For an empty input range return `begin` (== `end`). For a
   non-empty range the returned iterator is in `(begin, end]`, and `returned - begin` is the number of kept elements.
4. Elements in `[returned, end)` are left in an **unspecified** (valid but arbitrary) state; callers do not read them.
5. Only adjacent duplicates are removed: for the unsorted input `1 2 1 2` nothing is removed, for `3 3 1 1 2` the
   result is `3 1 2`.
6. Elements are only copied (assigned) and compared; the function never reorders kept elements.

## 3. Input specification

- `begin`, `end`: random-access iterators of type `I` (raw pointers into an array in this code base: `xpath_node*`; tests
  here use `int*` and a small struct pointer). `begin <= end`, the range may be empty.
- The element type provides copy assignment and `operator!=` (and `==`). No predicate argument exists.

## 4. Output specification

The iterator described in requirement 3. The array content is modified as in requirements 1, 2 and 4. No exceptions.

## 5. Edge cases and constraints

| input | kept prefix | returned `- begin` |
|---|---|---|
| (empty) | | 0 |
| `1` | `1` | 1 |
| `1 1` | `1` | 1 |
| `1 2 3 4 5` | `1 2 3 4 5` | 5 |
| `1 1 2 2 3 3` | `1 2 3` | 3 |
| `1 1 1 1` | `1` | 1 |
| `5 5 5 5 5 6` | `5 6` | 2 |
| `1 2 3 4 4` | `1 2 3 4` | 4 |
| `0 0 0 1 2 3` | `0 1 2 3` | 4 |

Single pass, linear time, no auxiliary memory. Arrays of millions of elements are processed; arrays without any
duplicates (nothing to remove) are by far the most common, and elements in front of the first duplicate must not be
copied needlessly.
