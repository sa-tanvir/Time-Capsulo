You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sortedlist.py`
- **Enclosing scope:** `class SortedList(MutableSequence)`

## Imports / includes available in this file

```
from __future__ import print_function
from bisect import bisect_left, bisect_right, insort
from itertools import chain, repeat, starmap
from math import log
from operator import add, eq, ne, gt, ge, lt, le, iadd
from textwrap import dedent
from functools import wraps
from sys import hexversion
```

The standard-library modules `sys` and `traceback` are not imported at module level but are
available: a solution may import them (for example inside the method, for the diagnostic dump).

## Other functions defined in the same file (signatures only; you may call them)

```
__make_cmp( seq_op , symbol , doc )
__make_cmp.comparer( self , other )
_build_index( self )
_check( self )
_delete( self , pos , idx )
_expand( self , pos )
_islice( self , min_pos , min_idx , max_pos , max_idx , reverse )
_loc( self , pos , idx )
_pos( self , idx )
_reset( self , load )
add( self , value )
append( self , value )
bisect_key_left( self , key )
bisect_key_right( self , key )
bisect_left( self , value )
bisect_right( self , value )
clear( self )
copy( self )
count( self , value )
discard( self , value )
extend( self , values )
identity( value )
index( self , value , start = None , stop = None )
insert( self , index , value )
irange( self , minimum = None , maximum = None , inclusive = ( True , True )
irange_key( self , min_key = None , max_key = None , inclusive = ( True , True )
islice( self , start = None , stop = None , reverse = False )
key( self )
pop( self , index = - 1 )
recursive_repr( fillvalue = '...' )
recursive_repr.decorating_function( user_function )
recursive_repr.recursive_repr.decorating_function.wrapper( self )
remove( self , value )
reverse( self )
update( self , iterable )
```


## Instance state and other members of the enclosing class and its bases (you may rely on them)

```
class SortedList(MutableSequence):
    DEFAULT_LOAD_FACTOR = 1000

    def __init__(self, iterable=None, key=None):
        assert key is None
        self._len = 0
        self._load = self.DEFAULT_LOAD_FACTOR
        self._lists = []
        self._maxes = []
        self._index = []
        self._offset = 0
        if iterable is not None:
            self._update(iterable)

    # aliases defined in the class body
    _clear = clear
    _update = update
    _getitem = __getitem__
    bisect = bisect_right
    _bisect_right = bisect_right


class SortedKeyList(SortedList):
    def __init__(self, iterable=None, key=identity):
        self._key = key
        self._len = 0
        self._load = self.DEFAULT_LOAD_FACTOR
        self._lists = []
        self._keys = []
        self._maxes = []
        self._index = []
        self._offset = 0
        if iterable is not None:
            self._update(iterable)

    # aliases defined in the class body
    _clear = clear
    _update = update
    _irange_key = irange_key
    bisect = bisect_right
    _bisect_key_left = bisect_key_left
    bisect_key = bisect_key_right
    _bisect_key_right = bisect_key_right
```

Meaning of the instance attributes (these invariants hold between public calls):

- `_lists`: list of non-empty Python lists ("sublists"). Each sublist is sorted, and the
  concatenation of all sublists, in order, is the whole sorted sequence. Empty container: `[]`.
- `_keys` (`SortedKeyList` only): same shape as `_lists`; `_keys[i][j] == self._key(_lists[i][j])`.
  A sorted-key list is ordered by these keys (ties keep no particular value order).
- `_maxes`: one entry per sublist; `_maxes[i]` is the last element of `_lists[i]`
  (for `SortedKeyList`: the last element of `_keys[i]`).
- `_len`: total number of stored values.
- `_load`: load factor (default 1000, at least 4). Every sublist holds at most `2 * _load`
  values, and every sublist except the last holds at least `_load // 2` values.
- `_index`, `_offset`: an optional positional index. When `_index` is empty, it has not been built
  (calling `self._build_index()` builds it). When non-empty it is a complete binary tree stored as a
  flat list (node `p` has children `2*p+1` and `2*p+2`): `_index[0] == _len`; the leaves
  `_index[_offset + i]` equal `len(_lists[i])` for every sublist `i`, so
  `len(_index) == _offset + len(_lists)`; each internal node `p < _offset` equals the sum of its
  existing children (only the left child if the right one is past the end, and 0 if neither exists).
- Helper semantics: `_loc(pos, idx)` converts a (sublist number, offset in sublist) pair into the
  flat index in the sorted sequence; `_pos(idx)` does the reverse for a non-negative or negative flat
  index; `_delete(pos, idx)` removes the value at that pair and restores all invariants;
  `_expand(pos)` restores invariants after sublist `pos` has grown.

=== STUB ===
```python
def _check(self):
    raise NotImplementedError  # TODO: implement according to the specification
```
