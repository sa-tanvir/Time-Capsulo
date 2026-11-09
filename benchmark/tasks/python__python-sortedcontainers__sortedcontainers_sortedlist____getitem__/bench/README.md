Workload: 12 seeded container recipes per size (n up to 1e3 / 1e4 / 1e5, load 4-1000, index pre-built or not,
every third a SortedKeyList, a few tiny/empty lists), each with 1500 queries: 60% integer indices (incl. negative and
out-of-range), 38% short slices, ~2% long slices with steps 1, -1, 2, -3, 7, n/3, and rare step-0 slices.
The driver builds lists up front and times only `sl[q]`; check mode hashes each result (type + repr) or error,
mutates returned lists to detect aliasing, and hashes the final contents.
