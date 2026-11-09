Workload: arrays whose equal values are adjacent (sorted node lists), to be compacted in place. S holds literal arrays (empty, single, all equal,
no duplicates, duplicates at the head/tail, even an unsorted array to show that only adjacent duplicates are removed) for `int` and for a two-field struct
(equality compares both fields); M/L add `G` lines that `driver.cpp` expands deterministically (splitmix64): 2*10^4 to 3*10^6 elements, run lengths
from all-distinct to long runs, with a long head run, one single run, or a duplicate pair at the very end.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified) and calls
`pugi::impl::unique(begin, end)` on a fresh copy of the array (made outside the timed region); the digest hashes the returned length and the kept prefix
(elements after the returned end are unspecified and not hashed).
