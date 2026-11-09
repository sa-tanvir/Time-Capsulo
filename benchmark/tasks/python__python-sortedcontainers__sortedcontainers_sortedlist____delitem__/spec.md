# Functional specification: `SortedList.__delitem__(self, index)`

## 1. Component overview

`SortedList` is a mutable sequence whose values are always kept in ascending order
(`SortedKeyList`, its subtype ordered by a key function, inherits this method unchanged). Values are
split across several sublists with bookkeeping described under "Instance state" in the context.
`__delitem__` implements `del sl[i]` and `del sl[start:stop:step]`: it removes values by position,
with exactly the semantics of `del` on a Python `list` holding the same sorted values. `SortedSet`
and the `SortedDict` views use it for positional deletion. Deleting a single position must cost
about logarithmic time; deleting a large slice should be efficient too (not one costly removal per
value when most of the list goes away).

## 2. Functional requirements

Let `seq` be the sorted sequence before the call and `n = len(self)`.

1. Integer `index`: remove `seq[index]` (negative indices count from the end). If out of range
   (`index >= n` or `index < -n`, including any index on an empty list) raise
   `IndexError('list index out of range')` and leave the list unchanged.
2. `slice` `index`: remove exactly the values at the positions `range(*index.indices(n))`, i.e. the
   list afterwards equals what `del lst[index]` would leave in a plain list copy `lst` of `seq`.
   Any `start`/`stop`/`step` combination is accepted (`None`, negative, out of range, positive or
   negative step). An empty selection leaves the list unchanged. `del sl[:]` empties the list.
3. A slice with `step == 0` raises `ValueError` (as raised by `slice.indices`) and leaves the list
   unchanged.
4. Return `None`.
5. After the call, all invariants listed in the context hold (`self._check()` passes): `_len`,
   `_maxes` (and `_keys` for key lists) are consistent, every sublist is non-empty and within the
   load-factor bounds, and the positional index is either consistent or empty (to be rebuilt
   lazily). The helpers `self._pos(i)` (flat index -> `(sublist, offset)`), `self._delete(pos, idx)`
   (remove one value and restore invariants), `self._getitem`, `self._clear()` and `self._update()`
   are available.

## 3. Input specification

- `self`: a valid `SortedList`/`SortedKeyList` of any size and load factor (>= 4), index built or not.
- `index`: an `int` or a `slice` object (with `int`/`None` fields).

## 4. Output specification

`None`; the effect is the in-place removal described above.

Examples:

```
sl = SortedList('abcde')
del sl[2]        # SortedList(['a', 'b', 'd', 'e'])
del sl[:2]       # SortedList(['d', 'e'])

sl = SortedList(range(100)); sl._reset(17)
del sl[10:40:1]  # removes 10..39 -> 70 values left
del sl[10:40:-1] # empty selection: no change
del sl[10:40:2]  # removes every other value among positions 10..39
del sl[10:40:-2] # empty selection: no change

sl = SortedList(range(100)); sl._reset(17)
while len(sl): del sl[random_position]; sl._check()   # stays valid down to empty
del SortedList(range(100))[:]                           # -> empty, valid

sl = SortedList(range(10)); del sl[::-3]   # removes 9, 6, 3, 0 -> [1, 2, 4, 5, 7, 8]
del SortedList()[0]                      # -> IndexError
```

## 5. Edge cases and constraints

- Deleting the only value, or the last values of the last sublist, must leave a valid (possibly
  empty) list.
- Small load factors (e.g. 4 or 17) mean many sublists; deletions spanning several sublists must
  keep the load-factor bounds.
- For `SortedKeyList` the keys must be removed together with their values.
- Not thread-safe; iterating the list while deleting is not supported.
