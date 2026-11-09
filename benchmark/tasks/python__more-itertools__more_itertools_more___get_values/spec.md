# Functional specification: `bucket._get_values(self, value)`

## 1. Component overview

`bucket(iterable, key, validator=None)` splits one source iterable into
several lazily-produced child iterators, one per key value ("bucket").
`bucket[value]` returns the child iterator for `value`; for values accepted by
the validator it is the iterator returned by `_get_values(self, value)`, the
method to implement. The other members of the class are shown in
`context.md`; the object state they rely on is:

- `self._it`: the shared source iterator;
- `self._key`: the key function, applied to a source item to get its bucket;
- `self._cache`: a `collections.defaultdict(deque)` mapping a bucket value to
  the items already pulled from the source for that bucket but not yet
  handed out (oldest first);
- `self._validator`: a one-argument predicate saying which bucket values are
  legitimate (default: everything).

## 2. Functional requirements

1. Return an iterator (normally a generator) that yields, in source order,
   every item `x` of the source with `self._key(x) == value`, each exactly
   once across all child iterators created for that value.
2. Pending items already stored in `self._cache[value]` are handed out first,
   oldest first, and removed from the cache as they are handed out. The cache
   must be consulted on **every** step, not only at creation time, because
   other children (and `__contains__`, which pushes an item back to the
   **front** of `self._cache[value]`) can change it between steps.
3. When no pending item exists for `value`, advance the shared source just far
   enough to find the next item whose key equals `value`, and yield it.
   Every item passed over on the way whose key `k` is accepted by
   `self._validator(k)` is appended to `self._cache[k]` (so other buckets
   can deliver it later, in order). Items whose key is rejected by the
   validator are discarded and must not create a cache entry.
4. When the source is exhausted and nothing is pending for `value`, the child
   iterator ends.
5. Laziness: the source is advanced only when an item is requested from the
   child and nothing is pending; never further than the next match. This
   makes infinite sources usable.
6. Examples (`key = lambda x: 10 * (x // 10)`, source
   `[10, 20, 30, 11, 21, 31, 12, 22, 23, 33]`):
   - `list(D[10])` gives `[10, 11, 12]`; afterwards `list(D[30])` gives
     `[30, 31, 33]`, `list(D[20])` gives `[20, 21, 22, 23]` and `list(D[40])`
     gives `[]`.
   - `10 in D` is `True`, `40 in D` is `False`, `21 in D` is `False`, and
     after these membership tests `next(D[10])` still gives `10`.
   - With source `itertools.count(0)`, `key = lambda x: int(str(x)[0])` and
     `validator = lambda x: 0 < x < 10`: the first three items of `D[1]` are
     `[1, 10, 11]`; afterwards `0` is not a key of `D._cache` (item `0` had a
     rejected key and was discarded).

## 3. Input specification

| Parameter | Type | Meaning |
|-----------|------|---------|
| `self` | `bucket` instance | Holds the shared state described in §1. |
| `value` | hashable | The bucket value to deliver; compared with `==` to `self._key(item)`. |

## 4. Output specification

An iterator over the source items belonging to bucket `value`, in source
order. Side effects: items of other (valid) buckets read on the way are
appended to their cache queues; delivered items are removed from the
cache.

## 5. Edge cases and constraints

- A bucket that never occurs exhausts the whole source (caching everything
  valid) and yields nothing.
- Several child iterators (for the same or different values) may be
  interleaved arbitrarily; together they never duplicate or lose an item.
- Exceptions raised by the source or by `self._key` propagate.
- Not thread-safe.
