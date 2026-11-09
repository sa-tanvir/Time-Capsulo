# Functional specification: `SortedList._check(self)`

## 1. Component overview

`SortedList` keeps its values in ascending order, split into several sorted sublists with extra
bookkeeping: per-sublist maxima, a total length, a load factor and an optional positional index
(all described under "Instance state" in the context). `_check` is the self-test used by the test
suite after every mutation: it verifies that the internal representation is consistent and fails
loudly if it is not. It returns nothing on success. Its cost should be linear in the number of
stored values.

## 2. Functional requirements

Verify **all** of the following conditions; if any one fails, the call must fail with
`AssertionError` (see requirement 10):

1. The load factor `_load` is at least 4.
2. There are as many entries in `_maxes` as there are sublists in `_lists`.
3. `self._len` equals the total number of values over all sublists.
4. Every sublist is non-decreasing: each element is `<=` the next one in the same sublist.
5. Across sublists the order continues: the last element of each sublist is `<=` the first element of
   the following sublist.
6. For every sublist `i`, `self._maxes[i] == self._lists[i][-1]`.
7. Every sublist holds at most `2 * self._load` values.
8. Every sublist except the last holds at least `self._load // 2` values (no constraint on the last).
9. Only when `self._index` is non-empty (an empty index means "not built" and is always valid):
   - the root (first entry) of the index equals the total length `_len`;
   - the index has exactly `_offset` internal entries followed by one leaf per sublist (its length is
     the offset plus the number of sublists);
   - the leaf of sublist `i` (entry number `_offset + i`) equals that sublist's length;
   - for every internal node `p` in `range(self._offset)`, with children `c = 2*p + 1` and `c + 1`:
     if `c` is past the end of the index the node must be `0`; if only `c` exists the node must equal
     `self._index[c]`; otherwise it must equal `self._index[c] + self._index[c + 1]`.

Failure behaviour:

10. When a condition fails, an `AssertionError` propagates to the caller. Any other exception raised
   while checking (for example from comparing values or indexing a malformed structure) also
   propagates unchanged. Before propagating any exception, the method writes a diagnostic dump to
   standard output: the traceback, followed by one line per attribute, each made of a label and the
   value — in this order: `len`, `load`, `offset`, `len_index` (length of the index), `index`,
   `len_maxes`, `maxes`, `len_lists`, `lists` (e.g. `print('len', self._len)`). The exact text of the
   dump is not checked.
11. On success return `None` and print nothing.
12. Never modify the object (in particular, do not build the positional index).

## 3. Input specification

- `self`: a `SortedList` (or subclass instance) whose attributes `_len`, `_load`, `_lists`,
  `_maxes`, `_index`, `_offset` exist; the values may or may not satisfy the invariants. Stored values
  are mutually comparable with `<=` and `==`.

## 4. Output specification

`None` on success; otherwise an exception (normally `AssertionError`) after the stdout dump.

Examples:

```
sl = SortedList(range(10)); sl._reset(4); sl._check()       -> None
sl = SortedList([0]); sl._reset(4); sl._build_index(); sl._check()   -> None
SortedList()._check()                                         -> None (empty list is valid)

sl = SortedList(range(10)); sl._reset(4)
sl._len = 5
sl._check()          -> AssertionError (length mismatch)

sl = SortedList(range(100)); sl._reset(10); sl._load = 3
sl._check()          -> AssertionError (load factor below 4)
```

## 5. Edge cases and constraints

- Empty list (`_lists == []`, `_maxes == []`, `_index == []`, `_len == 0`) is valid.
- A single sublist may hold fewer than `_load // 2` values.
- Duplicated values are allowed anywhere (all orderings are non-strict).
- When the index is non-empty, the tree may contain padding nodes that have no children; they must be
  `0`.
- Not thread-safe; read-only with respect to the object.
