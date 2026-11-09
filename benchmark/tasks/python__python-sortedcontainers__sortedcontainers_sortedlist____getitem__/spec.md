# Functional specification: `SortedList.__getitem__(self, index)`

## 1. Component overview

`SortedList` is a sequence whose values are always kept in ascending order (`SortedKeyList`, its
subtype, orders by a key function and inherits this method unchanged). The values are split across
several sublists with bookkeeping described under "Instance state" in the context. `__getitem__`
implements `sl[i]` and `sl[start:stop:step]` with exactly the semantics of a Python `list` holding the
same sorted values. It is also reachable as `self._getitem` and is used by `SortedSet` indexing,
the `SortedDict` keys/items/values views, `SortedDict.peekitem`, and slice deletion. Positional
lookups must be fast: logarithmic in the size for a single index, and proportional to the output
length (not the list length) for slices.

## 2. Functional requirements

Let `seq` be the sorted sequence (concatenation of the sublists) and `n = len(self)`.

1. Integer `index`: return `seq[index]`. Negative indices count from the end (`-1` is the last value).
   Out of range (`index >= n` or `index < -n`, including every index on an empty list): raise
   `IndexError` with the message `list index out of range`.
2. `slice` `index`: return a **new plain `list`** equal to `seq[index]` as Python list slicing would
   produce it, for every combination of `start`, `stop`, `step` (each may be `None`, negative, or out
   of range; they are normalised like `slice.indices(n)`):
   - positive steps give values in ascending order, negative steps in descending order;
   - empty selections give `[]`;
   - a full slice `sl[:]` returns a list of all values (a fresh list, never an internal sublist).
3. A slice with `step == 0` raises `ValueError` (the same error `slice.indices` raises: `slice step
   cannot be zero`).
4. Returned lists must never alias internal storage: mutating the result must not affect the sorted
   list.
5. The method does not change the list's contents. It may build the lazy positional index (the helper
   `self._pos(i)` maps a flat index to a `(sublist, offset)` pair and builds it if needed); all
   invariants in the context must still hold afterwards.

## 3. Input specification

- `self`: a valid `SortedList`/`SortedKeyList` of any size and load factor (>= 4), index built or not.
- `index`: an `int` or a `slice` object (with `int`/`None` fields).

## 4. Output specification

A single stored value for an integer index; a new `list` for a slice.

Examples:

```
sl = SortedList('abcde')
sl[1]      -> 'b'
sl[-1]     -> 'e'
sl[2:5]    -> ['c', 'd', 'e']
sl[::-2]   -> ['e', 'c', 'a']
sl[4:1:-1] -> ['e', 'd', 'c']
sl[3:1]    -> []

sl = SortedList(range(4))
sl[a:b:c] == list(range(4))[a:b:c]
    for a, b in [-6, -4, -2, 0, 2, 4, 6] and c in [-3, -2, -1, 1, 2, 3]

SortedList(range(100))[::0]   -> ValueError
SortedList()[5]               -> IndexError
SortedList(range(100))[200]   -> IndexError
SortedList(range(100))[-101]  -> IndexError
```

## 5. Edge cases and constraints

- Very small load factors (e.g. 4 or 17) produce many sublists; slices spanning many sublists, or
  starting/ending exactly on sublist boundaries, must be correct.
- Index `0` and `-1` on a non-empty list are the minimum and maximum values.
- For `SortedKeyList`, returned objects are the stored values (not their keys).
- Not thread-safe; the list must not be modified concurrently.
