Workload: 12 seeded container recipes per size (n up to 1e3 / 1e4 / 1e5, load factors 4-1000 so the number of
sublists ranges from 1 to ~25k, index pre-built or not, every third one a SortedKeyList, a few tiny/empty lists),
each with 2000 flat indices (70% non-negative, negative, ~10% out of range). The driver builds the lists up front and
times only `sl._pos(i)`; check mode hashes each (pos, idx) pair or the IndexError message, plus the sublists.
