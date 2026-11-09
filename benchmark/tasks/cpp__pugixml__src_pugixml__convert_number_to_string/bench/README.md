Workload: lists of doubles converted to XPath strings. S holds literal values given as exact IEEE-754 bit patterns (zeros, powers of ten, integers around
2^53, fractions, DBL_MAX, denormals, NaN, +-Infinity) plus one list evaluated with an allocator that cannot provide memory; M/L add `G` lines that `driver.cpp` expands
deterministically (splitmix64): 5*10^3 to 2*10^5 values per case, drawn from the full exponent range, big integers, short decimals, or specials and powers of ten.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified) and calls
`pugi::impl::convert_number_to_string(value, &alloc)` with a stack-based `xpath_allocator`; each result's text is hashed (FNV-1a) as part of the call loop. The allocator page is rewound
before every conversion.
