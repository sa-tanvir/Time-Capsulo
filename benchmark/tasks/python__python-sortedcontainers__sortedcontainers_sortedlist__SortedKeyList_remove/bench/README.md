Workload: 12 seeded SortedKeyList recipes per size (n up to 1e3 / 1e4 / 1e5, key neg, v//3 or v%101, load 4-1000,
index pre-built or not, a few tiny/empty lists), each with n/8+50 values to remove (present, absent, key present
but value absent; absent ones raise ValueError). Each repetition rebuilds the list outside the timer and times only
the `skl.remove(v)` calls (with try/except); check mode hashes (result or ValueError message, len) after every
call and the final contents.
