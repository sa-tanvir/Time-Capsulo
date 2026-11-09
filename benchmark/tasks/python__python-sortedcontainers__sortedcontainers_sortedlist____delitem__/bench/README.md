Workload: 12 seeded container recipes per size (n up to 1e3 / 1e4 / 1e5, load 4-1000, index pre-built or not,
every third a SortedKeyList, a few tiny/empty lists), each with n/10+30 deletions: 85% single indices (incl. negative,
~4% out of range), short slices with steps 1/-1/2/-3, occasional bulk slices and rare step-0 slices.
Each repetition rebuilds the list outside the timer and times only the `del sl[q]` calls; check mode hashes
the outcome and length after every deletion and the final contents.
