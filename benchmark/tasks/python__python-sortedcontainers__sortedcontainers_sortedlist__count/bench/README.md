Workload: 12 seeded SortedKeyList recipes per size (n up to 1e3 / 1e4 / 1e5, 0.3-4 copies per distinct value,
key neg, v//3 or v%101 -- the last gives large key groups of mixed values -- load factors 4-1000, index pre-built
or not, a few tiny/empty lists), each with 400 query values (present, absent, key-present-but-value-absent).
The driver builds the lists up front and times only `skl.count(value)`; check mode hashes all counts and the contents.
