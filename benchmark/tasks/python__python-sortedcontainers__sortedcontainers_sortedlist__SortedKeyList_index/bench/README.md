Workload: 12 seeded container recipes per size (n up to 1e3 / 1e4 / 1e5 values, 0.3-4 copies per distinct value,
load factors 4-1000, positional index pre-built or not, a few tiny/empty lists; key lists use neg, v//3 or v%101)
with 400 `(value, start, stop)` queries each: present/absent values, None/positive/negative/out-of-range bounds.
The driver builds the containers up front and times only `sl.index(value, start, stop)` calls;
check mode hashes each result or the ValueError message, plus the final list contents.
