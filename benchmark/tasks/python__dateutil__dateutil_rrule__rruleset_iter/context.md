# Context for the function to implement

- **Language:** python
- **File:** `dateutil/rrule.py`
- **Enclosing scope:** `class rruleset(rrulebase)`

## Imports / includes available in this file

```
import itertools
import datetime
import calendar
import re
import sys
from six import advance_iterator, integer_types
from six.moves import _thread, range
import heapq
from ._common import weekday as weekdaybase
from warnings import warn
```

## Other functions defined in the same file (signatures only; you may call them)

```
__construct_byset( self , start , byxxx , base )
__mod_distance( self , value , byxxx , base )
_handle_BYWEEKDAY( self , rrkwargs , name , value , ** kwargs )
_handle_FREQ( self , rrkwargs , name , value , ** kwargs )
_handle_UNTIL( self , rrkwargs , name , value , ** kwargs )
_handle_WKST( self , rrkwargs , name , value , ** kwargs )
_handle_int( self , rrkwargs , name , value , ** kwargs )
_handle_int_list( self , rrkwargs , name , value , ** kwargs )
_invalidate_cache( self )
_invalidates_cache( f )
_invalidates_cache.inner_func( self , * args , ** kwargs )
_iter( self )
_iter_cached( self )
_parse_date_value( self , date_value , parms , rule_tzids , ignoretz , tzids , tzinfos )
_parse_rfc( self , s , dtstart = None , cache = False , unfold = False , forceset = False , compatible = False , ignoretz = False , tzids = None , tzinfos = None )
_parse_rfc_rrule( self , line , dtstart = None , cache = False , ignoretz = False , tzinfos = None )
after( self , dt , inc = False )
before( self , dt , inc = False )
between( self , after , before , inc = False , count = 1 )
count( self )
ddayset( self , year , month , day )
exdate( self , exdate )
exrule( self , exrule )
htimeset( self , hour , minute , second )
mdayset( self , year , month , day )
mtimeset( self , hour , minute , second )
rdate( self , rdate )
rebuild( self , year , month )
replace( self , ** kwargs )
rrule( self , rrule )
stimeset( self , hour , minute , second )
wdayset( self , year , month , day )
xafter( self , dt , count = None , inc = False )
ydayset( self , year , month , day )
```

## Instance state and other members of the enclosing class (you may rely on them)

`rruleset` stores the four kinds of members as plain lists (filled by the public adders, in the
order they were added; nothing is sorted on insertion):

```
class rruleset(rrulebase):
    def __init__(self, cache=False):
        super(rruleset, self).__init__(cache)
        self._rrule = []    # inclusion rules (rrule objects; iterable, ascending occurrences)
        self._rdate = []    # inclusion datetimes (any order, may contain duplicates)
        self._exrule = []   # exclusion rules (rrule objects)
        self._exdate = []   # exclusion datetimes (any order, may contain duplicates)

    @_invalidates_cache
    def rrule(self, rrule):   self._rrule.append(rrule)
    @_invalidates_cache
    def rdate(self, rdate):   self._rdate.append(rdate)
    @_invalidates_cache
    def exrule(self, exrule): self._exrule.append(exrule)
    @_invalidates_cache
    def exdate(self, exdate): self._exdate.append(exdate)
```

Nested helper class `rruleset._genitem` (available as `self._genitem`) wraps an iterator so it
can live in a `heapq` heap ordered by its current value:

```
    class _genitem(object):
        def __init__(self, genlist, gen):
            try:
                self.dt = advance_iterator(gen)   # first value of the iterator
                genlist.append(self)              # only appended if the iterator is non-empty
            except StopIteration:
                pass
            self.genlist = genlist
            self.gen = gen

        def __next__(self):
            # advance to the next value; when the iterator is exhausted the item
            # removes itself from genlist (heappop if it is genlist[0], otherwise
            # remove + heapify), so genlist stays a valid heap
            try:
                self.dt = advance_iterator(self.gen)
            except StopIteration:
                if self.genlist[0] is self:
                    heapq.heappop(self.genlist)
                else:
                    self.genlist.remove(self)
                    heapq.heapify(self.genlist)

        next = __next__

        # comparisons delegate to the current value
        def __lt__(self, other): return self.dt < other.dt
        def __gt__(self, other): return self.dt > other.dt
        def __eq__(self, other): return self.dt == other.dt
        def __ne__(self, other): return self.dt != other.dt
```

Note: after advancing an item that is still alive, it keeps its old heap position; the caller is
responsible for restoring the heap order (e.g. `heapq.heapreplace(lst, item)` when it is `lst[0]`).
`advance_iterator(x)` (from `six`) is the builtin `next(x)`.

Base class `rrulebase` (how `_iter` is used):

```
class rrulebase(object):
    def __init__(self, cache=False):
        if cache:
            self._cache = []
            self._cache_lock = _thread.allocate_lock()
            self._invalidate_cache()
        else:
            self._cache = None
            self._cache_complete = False
            self._len = None

    def __iter__(self):
        if self._cache_complete:
            return iter(self._cache)
        elif self._cache is None:
            return self._iter()          # uncached: a fresh generator each time
        else:
            return self._iter_cached()   # cached: pulls from self._cache_gen (= self._iter())

    def _invalidate_cache(self):         # called after every rrule/rdate/exrule/exdate addition
        if self._cache is not None:
            self._cache = []
            self._cache_complete = False
            self._cache_gen = self._iter()
            if self._cache_lock.locked():
                self._cache_lock.release()
        self._len = None

    def count(self):
        if self._len is None:
            for x in self:
                pass
        return self._len                  # relies on _iter() setting self._len at exhaustion
```

`_iter_cached` fills `self._cache` from `self._cache_gen` in chunks under `self._cache_lock`,
marks `_cache_complete` when the generator is exhausted, and replays from the cache afterwards.
`before`, `after`, `xafter`, `between`, `__contains__` and `__getitem__` all iterate `self`.
