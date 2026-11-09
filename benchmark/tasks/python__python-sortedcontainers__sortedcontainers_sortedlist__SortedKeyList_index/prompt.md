You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sortedlist.py`
- **Enclosing scope:** `class SortedKeyList(SortedList)`

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
def index(self, value, start=None, stop=None):
    raise NotImplementedError  # TODO: implement according to the specification
```
