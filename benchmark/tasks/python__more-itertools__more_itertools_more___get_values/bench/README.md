Workload: seeded integer sources (up to 400 / 6k / 60k items for S/M/L) bucketed by x % k (k in 2..50),
40% with an "odd buckets only" validator. Each case runs an access plan that interleaves partial reads,
full drains, `in` probes and requests for never-occurring buckets across child iterators.
The target is reached through `bucket[...]` (its only public route). Check mode hashes all delivered items
plus the non-empty pending cache queues at the end.
