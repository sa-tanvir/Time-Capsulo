You are an expert Python developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing Python code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```python code block, with no explanation.

=== SPECIFICATION ===
# Functional specification

## 1. Component overview

`rruleset._iter(self)` is the occurrence generator of `dateutil.rrule.rruleset`, the RFC 5545 style "recurrence set" that combines several inclusion rules (`rrule` objects added with `.rrule()`), individual inclusion dates (`.rdate()`), exclusion rules (`.exrule()`) and individual exclusion dates (`.exdate()`). The base class `rrulebase` uses `_iter()` for everything: plain iteration (`list(rset)`, `for dt in rset`), the result cache (when `cache=True`), `count()`, `before()`, `after()`, `between()`, `in`, indexing. It must be a generator function.

## 2. Functional requirements

The generator yields every datetime that is produced by at least one inclusion source (any rrule in `self._rrule` or any datetime in `self._rdate`) and that is **not** produced by any exclusion source (any rrule in `self._exrule` or any datetime in `self._exdate`).

- **Order:** values are yielded in ascending chronological order, merging all inclusion sources.
- **No duplicates:** a datetime produced by several inclusion sources (or listed several times as an rdate, or produced by an rrule and also given as an rdate) is yielded once.
- **Exclusion by equality:** a candidate is suppressed if it equals (`==`) some exdate or some occurrence of some exrule. Exclusion sources never add values. Exdates and rdates may have been added in any order (e.g. exdates added in reverse chronological order still work).
- **Laziness:** sources are consumed on demand, only as far as needed to decide the next value, so sets containing unbounded rrules (no `count`/`until`) can be iterated partially (e.g. with `itertools.islice` or `rset.after(...)`), including unbounded exrules.
- **Length bookkeeping:** when (and only when) the generator runs to completion, it stores the number of values it yielded in `self._len` (used by `count()`); partial iteration leaves `self._len` unchanged.
- The rrule sources are iterated via their normal iteration protocol (`iter(rule)`), so their own caching applies. The stored `_rdate` / `_exdate` lists may be sorted in place; they are otherwise not modified, and no rules or dates are added or removed.

Examples (all at 09:00):
- rrules `YEARLY count=2 byweekday=TU` and `YEARLY count=1 byweekday=TH`, both from 1997-09-02 -> 1997-09-02, 1997-09-04, 1997-09-09.
- rrule `YEARLY count=1 byweekday=TU` from 1997-09-02 plus rdates 1997-09-04, 1997-09-09 -> 1997-09-02, 09-04, 09-09.
- rrule `YEARLY count=6 byweekday=(TU,TH)` from 1997-09-02 with exrule `YEARLY count=3 byweekday=TH` (same start) -> 1997-09-02, 09-09, 09-16; afterwards `count()` is 3.
- Same rrule with exdates 09-04, 09-11, 09-18 -> 1997-09-02, 09-09, 09-16.
- rdates 09-02, 09-04, 09-09, 09-11, 09-16, 09-18 with exdates 09-04, 09-11, 09-18 -> 09-02, 09-09, 09-16.
- `MONTHLY count=5 bymonthday=10` from 2004-01-01 09:00 with exdates 2004-04-10 09:00 then 2004-02-10 09:00 -> 2004-01-10, 2004-03-10, 2004-05-10.
- Two rrules (`YEARLY count=2 byweekday=TH` from 1983-04-01; `WEEKLY count=4 byweekday=FR` from 1991-06-03): 6 values; adding exdate 1991-06-28 gives 5.

## 3. Input specification

No arguments besides `self`. It reads the instance lists `self._rrule`, `self._rdate`, `self._exrule`, `self._exdate` (see context). All datetimes involved (rule occurrences, rdates, exdates) must be mutually comparable (all naive or all aware); every rrule yields its occurrences in ascending order.

## 4. Output specification

A generator object yielding `datetime.datetime` values as described. On normal completion it sets `self._len` to an `int` (0 for an empty set) and then finishes (raises `StopIteration` to the consumer).

## 5. Edge cases and constraints

- Empty set (nothing added, or only exclusions): yields nothing and sets `self._len = 0`.
- Only rdates: they are yielded sorted and deduplicated, minus exdates.
- An exclusion that matches nothing, or lies before/after all inclusions, has no effect.
- If every inclusion value is excluded, nothing is yielded and `_len` becomes 0.
- Comparing naive with aware datetimes raises `TypeError` (from the comparison), propagated to the consumer.
- The generator body starts executing on the first `next()`; the source lists are read at that point. Mutating the set (adding rules/dates) while a generator is active is not supported.
- Not thread-safe by itself; the base class's cached iteration serialises access with a lock.

=== CONTEXT ===
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

=== STUB ===
```python
def _iter(self):
    raise NotImplementedError  # TODO: implement according to the specification
```
