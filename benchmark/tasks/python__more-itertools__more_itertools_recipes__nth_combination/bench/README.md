Workload: seeded (n, r, index) triples with pools range(n), n up to 60 / 300 / 1200 (S/M/L);
indices are uniform over all C(n, r) combinations (often huge big-ints, stored as decimal strings),
30% given as negative indices, plus ~4% invalid r (ValueError) and ~4% out-of-range index (IndexError).
The driver calls nth_combination(pool_tuple, r, index); check mode hashes repr() of the tuple or the error type name.
