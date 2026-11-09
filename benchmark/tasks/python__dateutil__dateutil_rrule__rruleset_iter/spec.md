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
