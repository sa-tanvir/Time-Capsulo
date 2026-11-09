Workload: integer arrays to be sorted in place. S holds literal arrays (empty, single, pairs, runs of equal values, extremes of `int`,
lengths around the 16-element threshold) in three flavours: ascending `int`, descending `int` (predicate `a > b`), and a struct `{key, id}`
whose predicate orders by key and then by a unique id (so the sorted result is unique even for repeated keys); M/L add `G` lines
that `driver.cpp` expands deterministically (splitmix64): 10^4 to 7*10^5 elements in eight patterns (random, ascending, descending, all equal,
eight distinct values, sawtooth, nearly sorted, many duplicates).
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified) and calls
`pugi::impl::sort(begin, end, pred)` on a fresh copy of the array (the copy is made outside the timed region); the digest hashes the sorted array.
