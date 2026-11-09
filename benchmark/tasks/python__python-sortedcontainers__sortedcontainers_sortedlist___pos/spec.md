# Functional specification: `SortedList._pos(self, idx)`

## 1. Component overview

`SortedList` stores its sorted values split across several sublists (`self._lists`), with extra
bookkeeping described under "Instance state" in the context, including an optional, lazily built
positional index (`self._index`, `self._offset`). `_pos` translates a position in the flat sorted
sequence (what the user passes to `sl[i]`, `del sl[i]`, `sl.pop(i)`, `islice`, `SortedDict.peekitem`,
the `SortedDict` views, ...) into the pair `(pos, idx)` such that the value lives at
`self._lists[pos][idx]`. It is the inverse of `self._loc(pos, idx)`. It is called on every
positional access, so it must be fast: logarithmic in the number of sublists, not a scan over them
(building the positional index once and reusing it is allowed).

## 2. Functional requirements

Let `n = self._len` and let `seq` be the concatenation of all sublists.

1. Accept a non-negative `idx` with `0 <= idx < n` and return the unique pair `(pos, idx_in)` with
   `0 <= pos < len(self._lists)`, `0 <= idx_in < len(self._lists[pos])` and
   `self._lists[pos][idx_in] is seq[idx]` (i.e. `idx` equals the total length of sublists
   `0 .. pos-1` plus `idx_in`).
2. Accept a negative `idx` with `-n <= idx < 0`, meaning `n + idx` as for Python lists, and return the
   pair for that position.
3. Raise `IndexError('list index out of range')` when `idx >= n` or `idx < -n` (this includes any
   index on an empty list).
4. The returned value is a 2-tuple of `int`.
5. Contents and order of the list must not change. If the positional index is empty when needed, it
   may be built by calling `self._build_index()`; a non-empty index is valid and may be used as is.
   All invariants listed in the context must hold afterwards.

## 3. Input specification

- `self`: a valid `SortedList` or `SortedKeyList` (any size, load factor >= 4, any sublist sizes
  allowed by the invariants, positional index built or not).
- `idx`: an `int` (may be negative or far outside the valid range).

## 4. Output specification

A tuple `(pos, idx_in)` as defined above, or a raised `IndexError` with message
`list index out of range`.

Examples (sublists shown explicitly):

```
# self._lists == [[1, 2, 3], [4, 5], [6, 7, 8, 9], [10, 11, 12, 13, 14]], self._len == 14
_pos(0)    -> (0, 0)
_pos(2)    -> (0, 2)
_pos(3)    -> (1, 0)
_pos(8)    -> (2, 3)       # value 9
_pos(13)   -> (3, 4)       # value 14
_pos(-1)   -> (3, 4)
_pos(-5)   -> (3, 0)
_pos(-6)   -> (2, 3)
_pos(-14)  -> (0, 0)
_pos(14)   -> IndexError: list index out of range
_pos(-15)  -> IndexError: list index out of range

SortedList()._pos(0)   -> IndexError
SortedList()._pos(-1)  -> IndexError
```

Through the public API: `SortedList(range(100))[200]` and `[-101]` raise `IndexError`;
`sl.pop(-11)` / `sl.pop(10)` on a 10-element list raise `IndexError`.

## 5. Edge cases and constraints

- Single-sublist lists and lists with many tiny sublists (load factor 4) must both work.
- The answer depends only on the sublist lengths, never on the values.
- Do not modify `self._lists`, `self._maxes` or `self._len`.
- Not thread-safe; the list must not be modified concurrently.
