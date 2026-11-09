Workload: valid seeded containers (S 24 x n<=1e3, M 16 x n<=1e4, L 12 x n<=1e5; load 4-1000, index pre-built or not,
a few tiny/empty ones) plus 2 small (n<=300) containers per corruption kind
(length, load, maxes, maxes length, unsorted pair, oversize sublists, index root/leaf/inner node).
The driver builds/corrupts everything up front, redirects stdout to an in-memory sink, and times only `_check()`;
check mode hashes "None"/"AssertionError" per case plus the (unchanged) internal state.
