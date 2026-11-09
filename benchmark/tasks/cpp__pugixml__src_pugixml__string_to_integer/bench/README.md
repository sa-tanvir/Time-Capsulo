Workload: strings handed to `string_to_integer`. S holds the literal edge cases from the test suite (signs, whitespace, `0x`
prefixes, values at and just beyond each 32/64-bit limit, junk after the digits) and each literal is run for all four
instantiations (`int`, `unsigned`, `long long`, `unsigned long long`, as `get_value_int/uint/llong/ullong` call it). M/L add `G` lines that
`driver.cpp` expands deterministically (splitmix64): 10^4 to 1.5*10^6 characters of random decimal or hex digits, huge
runs of leading zeros followed by a short number, whitespace prefixes, negative values.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified)
and calls `pugi::impl::string_to_integer<U>(str, minv, maxv)` directly; the output digest hashes every returned value.
Inputs are expanded before timing.
