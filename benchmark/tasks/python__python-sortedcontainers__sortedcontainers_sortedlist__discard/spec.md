# Functional specification: `SortedKeyList.discard(self, value)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype that keeps its values ordered by `self._key(value)`, the
key function given at construction. Values whose keys are equal form one contiguous group; inside a
group the values are in no particular order and may differ from each other (with
`key=lambda x: x % 10`, the values `2` and `12` share a group). The values and their precomputed
keys are stored in parallel sublists with extra bookkeeping (see "Instance state" in the context).
`discard` removes one occurrence of `value` if it is present and silently does nothing otherwise
(the sorted-key counterpart of `set.discard`). It must locate the group via the key order, so the
expected cost is logarithmic in the list size plus the size of `value`'s key group (plus the cost of
the removal itself).

## 2. Functional requirements

1. Compute `k = self._key(value)` (one call is enough).
2. Find the first position, in sorted order, whose stored key equals `k` and whose stored value
   equals `value` (`==`). Values with the same key but not equal to `value` are skipped; values with
   a different key are never considered.
3. If such a position exists, remove exactly that one value (and its key). Other occurrences stay.
4. If no such position exists (empty list, key absent, or no equal value in the key group), do
   nothing.
5. Return `None` in all cases.
6. After the call every invariant listed in the context holds (`_check()` passes): lengths, sublist
   sizes relative to the load factor, `_maxes`, parallel `_keys`, and the positional index (either
   kept consistent or emptied so it is rebuilt lazily). The helper `_delete(pos, idx)` removes the
   value at a (sublist, offset) pair and restores these invariants.

## 3. Input specification

- `self`: a valid `SortedKeyList` of any size and load factor (>= 4), positional index built or not.
- `value`: any object accepted by the key function; its key is comparable with the stored keys.

## 4. Output specification

`None`; the effect is the in-place removal (or not) described above. `len(self)` decreases by 1 iff a
value was removed.

Examples (`modulo(x) == x % 10`, `neg(x) == -x`):

```
skl = SortedKeyList(key=modulo)
skl.discard(0)   -> None; len(skl) == 0

skl = SortedKeyList([1, 2, 2, 2, 3, 3, 5], key=modulo); skl._reset(4)
skl.discard(6)   # key 6 absent: no change
skl.discard(4)   # key 4 absent: no change
skl.discard(2)   # removes one 2
skl.discard(11); skl.discard(12); skl.discard(13); skl.discard(15)   # keys present, values absent
list(skl) == [1, 2, 2, 3, 3, 5]

skl = SortedKeyList([5, 4, 3, 2, 1], key=neg)
skl.discard(1); skl.discard(0)
list(skl) == [5, 4, 3, 2]
```

## 5. Edge cases and constraints

- Discarding the last remaining value leaves a valid empty list.
- The matching value may sit in a later sublist than the first value of its key group (small load
  factors such as 4); it must still be found.
- Never raises for a missing value (unlike `remove`); exceptions raised by the key function or by
  comparisons propagate unchanged.
- Not thread-safe; no concurrent modification or iteration is assumed.
