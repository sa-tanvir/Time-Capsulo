# Context for the function to implement

- **Language:** python
- **File:** `sortedcontainers/sorteddict.py`
- **Enclosing scope:** `class SortedDict(dict)`

## Imports / includes available in this file

```
import sys
import warnings
from .sortedlist import SortedList, recursive_repr
from .sortedset import SortedSet
```

## Other functions defined in the same file (signatures only; you may call them)

```
__make_raise_attributeerror( original , alternate )
__make_raise_attributeerror.method( self )
_check( self )
_from_iterable( cls , it )
_view_delitem( self , index )
clear( self )
copy( self )
fromkeys( cls , iterable , value = None )
iloc( self )
items( self )
key( self )
keys( self )
peekitem( self , index = - 1 )
pop( self , key , default = __not_given )
popitem( self , index = - 1 )
setdefault( self , key , default = None )
values( self )
```

## Instance state and other members of the enclosing class (you may rely on them)

`SortedDict` subclasses the built-in `dict` (which stores the items) and keeps the dict keys in a
`SortedList` (or `SortedKeyList` when a key function was given). `__init__` caches bound methods:

```
class SortedDict(dict):
    def __init__(self, *args, **kwargs):
        if args and (args[0] is None or callable(args[0])):
            _key = self._key = args[0]
            args = args[1:]
        else:
            _key = self._key = None

        self._list = SortedList(key=_key)

        _dict = super(SortedDict, self)
        self._dict_clear = _dict.clear
        self._dict_delitem = _dict.__delitem__
        self._dict_iter = _dict.__iter__
        self._dict_pop = _dict.pop
        self._dict_setitem = _dict.__setitem__
        self._dict_update = _dict.update

        _list = self._list
        self._list_add = _list.add
        self._list_clear = _list.clear
        self._list_iter = _list.__iter__
        self._list_reversed = _list.__reversed__
        self._list_pop = _list.pop
        self._list_remove = _list.remove
        self._list_update = _list.update
        # (public sorted-list methods such as bisect_left, index, irange, islice are also exposed)

        self._update(*args, **kwargs)

    def __setitem__(self, key, value):
        "Store item `(key, value)` in sorted dict."
        if key not in self:
            self._list_add(key)
        self._dict_setitem(key, value)

    _setitem = __setitem__
    _update = update   # alias defined right after `update` in the class body
```

Invariant between public calls: the set of dict keys equals the contents of `self._list`
(each key exactly once), and `self._list` is sorted (by `self._key(key)` when a key function is set).
