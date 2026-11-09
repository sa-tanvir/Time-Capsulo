Workload: seeded integer lists (up to 200 / 3k / 30k items for S/M/L) drained via list.pop, deque.popleft or
an iterator's __next__, with the end exception given exactly, as Exception, as a tuple, or wrongly (KeyError,
so the real error propagates); ~1/3 of cases also pass a `first` callable.
Fresh sources are built before the timed loop; check mode hashes repr() of each result or the error type name.
