# Functional specification: `SortedKeyList.index(self, value, start=None, stop=None)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype whose values are kept in ascending order of
`self._key(value)` (like `sorted(..., key=...)`). Values with equal keys form a contiguous group, but
inside such a group the values themselves are in no particular order. Internally the values (and
their keys) are split into several sublists plus bookkeeping (see "Instance state" in the context). `index` is the sorted-list counterpart of `list.index`: it returns the position of the
first occurrence of `value` inside an optional `[start, stop)` window of the sorted sequence, and
raises `ValueError` if there is none. It must exploit the sorted order: the expected cost is
logarithmic in the list size plus the size of the group of values sharing `value`'s key, not a
linear scan of the whole list.

## 2. Functional requirements

Let `n = len(self)` and let `seq` be the sorted sequence (the concatenation of the sublists).

1. Normalise the window bounds like slicing does, but with these exact rules:
   - `start is None` means `0`; a negative `start` has `n` added to it; if it is still negative it
     becomes `0`.
   - `stop is None` means `n`; a negative `stop` has `n` added to it (it is **not** clamped to 0 —
     it may stay negative); a `stop` greater than `n` becomes `n`.
2. An *occurrence* is a position `i` whose stored key equals `self._key(value)` and whose stored
   value satisfies `seq[i] == value`. Return the smallest occurrence `i` with `start <= i < stop`.
   The key function is called on `value` (once is enough); stored keys are already available.
3. If no such `i` exists, raise `ValueError` with the message `'{!r} is not in list'` formatted with
   `value` (for example `ValueError("'z' is not in list")`, `ValueError('0 is not in list')`). This
   includes: empty list, `value` absent, the normalised window being empty (`stop <= start`), and
   all occurrences of `value` lying outside the window.
4. Occurrences can only lie inside the group of positions whose key equals `self._key(value)`;
   values in that group that differ from `value` are skipped, and they may be interleaved with
   occurrences.
5. The method must not change the contents of the list. It may build the lazy positional index
   (`self._index`/`self._offset`) as a side effect; all invariants listed in the context must still
   hold afterwards.

## 3. Input specification

- `self`: a valid `SortedKeyList` (any key function returning comparable keys; any size, any load factor >= 4, positional index built or not).
- `value`: any object accepted by the key function; its key is comparable with the stored keys.
- `start`, `stop`: `None` or `int` (may be negative or far outside `[-n, n]`).

## 4. Output specification

An `int` in `[0, n)`, or a raised `ValueError` as described above.

Examples (`neg(x) == negate(x) == -x`, `modulo(x) == x % 10`):

```
skl = SortedKeyList([5, 4, 3, 2, 1], key=neg)
skl.index(2)             -> 3
skl.index(0)             -> ValueError: 0 is not in list

skl = SortedKeyList(range(100), key=negate); skl._reset(17)
skl.index(pos) == 99 - pos for every pos in range(100)   # list is 99, 98, ..., 0
skl.index(99, 0, 1000)   -> 0

skl = SortedKeyList(range(100), key=modulo); skl._reset(7)
# order: 0, 10, ..., 90, 1, 11, ..., 91, 2, ...
skl.index(9, 0, 1000)    -> 90
skl.index(91, 0, 15)     -> ValueError (91 is at position 19)

skl = SortedKeyList([0] * 100, key=modulo); skl._reset(7)
skl.index(0, start, stop + 1) == start   for 0 <= start <= stop < 100
skl.index(0, -(100 - start)) == start    for 0 <= start < 100
skl.index(0, -1000)      -> 0

skl = SortedKeyList([0] * 10, key=modulo)
skl.index(0, 10)         -> ValueError
skl.index(0, 0, -10)     -> ValueError
skl.index(0, 7, 3)       -> ValueError
skl.index(1)             -> ValueError
SortedKeyList(key=modulo).index(1)                         -> ValueError
SortedKeyList([0]*10 + [1]*10 + [2]*10, key=modulo).index(1, 0, 10) -> ValueError
SortedKeyList(range(10), key=modulo).index(4, 5)           -> ValueError
SortedKeyList(range(10), key=modulo).index(19)             -> ValueError (same key as 9, not equal)
```

## 5. Edge cases and constraints

- Empty list: always `ValueError`, whatever `start`/`stop` are.
- `start >= n` or `stop <= start` after normalisation: `ValueError`.
- Values that compare equal (e.g. `1` and `1.0`) and have the same key count as occurrences.
- A value whose key is present but which is not itself stored (e.g. `19` above) is not found.
- Must work for lists made of many sublists (small load factors such as 4 or 17), with or without a
  pre-built positional index.
- Not thread-safe; the list must not be modified concurrently.
