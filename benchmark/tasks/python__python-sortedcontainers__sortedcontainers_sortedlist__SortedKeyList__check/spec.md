# Functional specification: `SortedKeyList._check(self)`

## 1. Component overview

`SortedKeyList` is a `SortedList` subtype that keeps its values ordered by `self._key(value)`. Values
are stored in sublists, with the precomputed keys in parallel sublists `self._keys`, plus extra
bookkeeping: per-sublist maximum keys, a total length, a load factor and an optional positional index
(all described under "Instance state" in the context). `_check` is the self-test used by the test
suite after every mutation: it verifies that the internal representation is consistent and fails
loudly if it is not. It returns nothing on success. Its cost should be linear in the number of
stored values.

## 2. Functional requirements

Verify **all** of the following conditions; if any one fails, the call must fail with
`AssertionError` (see requirement 11):

1. The load factor `_load` is at least 4.
2. `_maxes`, `_lists` and `_keys` all have the same number of entries (one per sublist).
3. `self._len` equals the total number of values over all value sublists (`self._lists`).
4. Every key sublist is non-decreasing: each key is `<=` the next one in the same key sublist.
5. Across key sublists the order continues: the last key of each key sublist is `<=` the first key of
   the following key sublist.
6. Keys match values: for every `i`, `len(self._lists[i]) == len(self._keys[i])` and for every `j`,
   `self._key(self._lists[i][j]) == self._keys[i][j]`.
7. For every sublist `i`, `self._maxes[i] == self._keys[i][-1]` (the last **key**).
8. Every value sublist holds at most `2 * self._load` values.
9. Every value sublist except the last holds at least `self._load // 2` values (no constraint on the
   last).
10. Only when `self._index` is non-empty (an empty index means "not built" and is always valid):
   - the root (first entry) of the index equals the total length `_len`;
   - the index has exactly `_offset` internal entries followed by one leaf per sublist (its length is
     the offset plus the number of sublists);
   - the leaf of sublist `i` (entry number `_offset + i`) equals that sublist's length;
   - for every internal node `p` in `range(self._offset)`, with children `c = 2*p + 1` and `c + 1`:
     if `c` is past the end of the index the node must be `0`; if only `c` exists the node must equal
     `self._index[c]`; otherwise it must equal `self._index[c] + self._index[c + 1]`.

Failure behaviour:

11. When a condition fails, an `AssertionError` propagates to the caller. Any other exception raised
   while checking (for example from comparing values or indexing a malformed structure) also
   propagates unchanged. Before propagating any exception, the method writes a diagnostic dump to
   standard output: the traceback, followed by one line per attribute, each made of a label and the
   value — in this order: `len`, `load`, `offset`, `len_index` (length of the index), `index`,
   `len_maxes`, `maxes`, `len_keys`, `keys`, `len_lists`, `lists` (e.g. `print('len', self._len)`). The exact text of the
   dump is not checked.
12. On success return `None` and print nothing.
13. Never modify the object (in particular, do not build the positional index).

## 3. Input specification

- `self`: a `SortedKeyList` (or subclass instance) whose attributes `_key`, `_len`, `_load`,
  `_lists`, `_keys`, `_maxes`, `_index`, `_offset` exist; they may or may not satisfy the invariants.
  Keys are mutually comparable with `<=` and `==`; the key function is cheap and deterministic.

## 4. Output specification

`None` on success; otherwise an exception (normally `AssertionError`) after the stdout dump.

Examples (`modulo(x) == x % 10`, `neg(x) == -x`):

```
skl = SortedKeyList(range(10), key=modulo); skl._reset(4); skl._check()   -> None
SortedKeyList(key=neg)._check()                                          -> None

skl = SortedKeyList(range(10), key=modulo); skl._reset(4)
skl._len = 5
skl._check()         -> AssertionError (length mismatch)

skl = SortedKeyList(range(10), key=neg)
skl._keys[0][0] = 99
skl._check()         -> AssertionError (keys no longer sorted / no longer match values)
```

## 5. Edge cases and constraints

- Empty list (`_lists == _keys == _maxes == _index == []`, `_len == 0`) is valid.
- Values themselves are never compared with each other; only keys are ordered.
- A single sublist may hold fewer than `_load // 2` values.
- Duplicated keys and values are allowed anywhere (all orderings are non-strict).
- When the index is non-empty, the tree may contain padding nodes that have no children; they must be
  `0`.
- Not thread-safe; read-only with respect to the object.
