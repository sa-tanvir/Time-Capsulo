Workload: seeded integer sequences (up to 300 / 10k / 40k items for S/M/L), per-item or chunked
(chunk sizes 1-100), with/without before/after callbacks, ~25% of sources raising RuntimeError mid-stream.
The driver records the full interleaving of func/before/after calls and yielded items in one log list;
check mode hashes that log (so effect ordering is verified), time mode only measures the same loop.
