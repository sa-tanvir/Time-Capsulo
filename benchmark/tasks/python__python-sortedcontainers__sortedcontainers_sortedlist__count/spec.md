# Functional specification: `SortedKeyList.count(self, value)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype that keeps its values ordered by `self._key(value)`, the
key function given at construction (like `sorted(..., key=...)`). Values whose keys are equal form one
contiguous group; inside a group the values are in no particular order and may differ from each
other (e.g. with `key=lambda x: x % 10`, the values `3`, `13` and `23` share a group). The stored
values and their precomputed keys are kept in parallel sublists (see "Instance state" in the
context). `count` is the sorted-key counterpart of `list.count`: it returns how many stored values
are equal to `value`. It must use the key order to find the relevant group instead of scanning the
whole list: the expected cost is logarithmic in the list size plus the size of the group of values
sharing `value`'s key.

## 2. Functional requirements

1. Compute `k = self._key(value)` (one call is enough; stored keys are already available).
2. Return the number of stored positions whose stored key equals `k` **and** whose stored value
   equals `value` (`==`).
3. Values with a different key are never counted, even if they compare equal to `value`.
4. Values with the same key but not equal to `value` are skipped (they may be interleaved with equal
   ones).
5. The list is not modified (contents, order and internal bookkeeping stay valid).

## 3. Input specification

- `self`: a valid `SortedKeyList` of any size and load factor (>= 4), positional index built or not.
  The key function returns values that are totally ordered with each other.
- `value`: any object accepted by the key function.

## 4. Output specification

A non-negative `int`. Returns `0` for an empty list or when no stored value matches.

Examples (`neg(x) == -x`, `modulo(x) == x % 10`):

```
skl = SortedKeyList([4, 4, 4, 4, 3, 3, 3, 2, 2, 1], key=neg)
skl.count(2)  -> 2

skl = SortedKeyList(key=modulo); skl._reset(7)
skl.count(0)  -> 0
for i in range(100):
    for _ in range(i):
        skl.add(i)
skl.count(i) == i   for every i in range(100)   # e.g. count(13) == 13 although 3, 23, ... share its key

SortedKeyList(range(8), key=modulo).count(9)  -> 0   # key 9 absent
SortedKeyList(range(8), key=modulo).count(18) -> 0   # key 8 absent
SortedKeyList(range(20), key=modulo).count(25) -> 0  # key 5 present, but 25 is not stored
```

## 5. Edge cases and constraints

- Empty list: `0`.
- `value`'s key larger than every stored key, or falling between stored keys: `0`.
- Groups may span several internal sublists (small load factors such as 4 or 7); all matching
  values across sublist boundaries must be counted.
- Never raises for a value whose key is comparable with the stored keys; exceptions raised by the key
  function or by comparisons propagate unchanged.
- Not thread-safe; the list must not be modified concurrently.
