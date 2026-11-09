# Functional specification: `SortedKeyList.remove(self, value)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype that keeps its values ordered by `self._key(value)`, the
key function given at construction. Values whose keys are equal form one contiguous group; inside a
group the values are in no particular order and may differ from each other (with
`key=lambda x: x % 10`, the values `2` and `12` share a group). The values and their precomputed
keys are stored in parallel sublists with extra bookkeeping (see "Instance state" in the context).
`remove` deletes one occurrence of `value`, which must be a member; otherwise it raises
`ValueError` (the sorted-key counterpart of `list.remove`). It must locate the group via the key
order, so the expected cost is logarithmic in the list size plus the size of `value`'s key group
(plus the cost of the removal itself).

## 2. Functional requirements

1. Compute `k = self._key(value)` (one call is enough; for an empty list the key function need
   not be called at all).
2. Find the first position, in sorted order, whose stored key equals `k` and whose stored value
   equals `value` (`==`). Values with the same key but not equal to `value` are skipped; values with
   a different key are never considered.
3. If such a position exists, remove exactly that one value (and its key) and return `None`. Other
   occurrences of equal values stay.
4. If no such position exists, raise `ValueError` with the message `'<repr(value)> not in list'`
   (e.g. `ValueError('0 not in list')`, `ValueError("'a' not in list")`). This covers: the list is
   empty; `k` is greater than every stored key; no stored key equals `k`; the key group exists but
   contains no value equal to `value` (also when that group runs up to the very end of the list).
   When the error is raised the list is unchanged.
5. After a successful call every invariant listed in the context holds (`_check()` passes):
   lengths, sublist sizes relative to the load factor, `_maxes`, parallel `_keys`, and the positional
   index (either kept consistent or emptied so it is rebuilt lazily). The helper `_delete(pos, idx)`
   removes the value at a (sublist, offset) pair and restores these invariants.

## 3. Input specification

- `self`: a valid `SortedKeyList` of any size and load factor (>= 4), positional index built or not.
- `value`: any object accepted by the key function; its key is comparable with the stored keys.

## 4. Output specification

`None` on success; the effect is the in-place removal of one value, so `len(self)` decreases by 1.
On failure `ValueError` as described above and no change.

Examples (`modulo(x) == x % 10`, `neg(x) == -x`):

```
skl = SortedKeyList([1, 2, 3, 4, 5], key=neg)
skl.remove(5)            # -> None
list(skl) == [4, 3, 2, 1]
skl.remove(0)            # ValueError: 0 not in list

skl = SortedKeyList([1, 2, 2, 2, 3, 3, 5], key=modulo); skl._reset(4)
skl.remove(2)
list(skl) == [1, 2, 2, 3, 3, 5]

SortedKeyList(key=modulo).remove(0)                       # ValueError (empty)
SortedKeyList([1, 2, 2, 2, 3, 3, 5], key=modulo).remove(4)  # ValueError (key 4 absent)
SortedKeyList([1, 1, 1, 2, 2, 2], key=modulo).remove(13)    # ValueError (key 3 beyond all keys)
SortedKeyList([1, 1, 1, 2, 2, 2], key=modulo).remove(12)    # ValueError (key 2 present, value absent,
                                                            #   group reaches the end of the list)
skl = SortedKeyList(range(100), key=modulo); skl._reset(10)
skl.remove(100)          # ValueError (key 0 group is 0, 10, ..., 90; 100 is not in it)

skl = SortedKeyList(range(20), key=neg); skl._reset(4)
for v in range(20): skl.remove(v)     # every call succeeds; afterwards
len(skl) == 0 and skl._lists == [] and skl._maxes == []
```

## 5. Edge cases and constraints

- Removing the last remaining value leaves a valid empty list (`_lists`, `_keys`, `_maxes` empty).
- The matching value may sit in a later sublist than the first value of its key group (small load
  factors such as 4); it must still be found.
- Exceptions raised by the key function or by comparisons propagate unchanged.
- Not thread-safe; no concurrent modification or iteration is assumed.
