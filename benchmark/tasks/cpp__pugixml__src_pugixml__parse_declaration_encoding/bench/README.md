Workload: byte buffers that start like XML declarations. S holds literal cases (valid declarations with various quotes, spacing and
symbol characters, missing/unterminated/misplaced encoding attributes, truncated buffers, near-misses such as `enable=`);
M/L add `G` lines that `driver.cpp` expands deterministically (splitmix64): `<?xml version="1.0"` followed by 2*10^4 to 2.5*10^6 filler
characters (containing no `?` and no `n`, so the whole filler is scanned) and one of six tails (valid, no attribute, `enable=`, unterminated, no `=`, no quote).
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified) and calls
`pugi::impl::parse_declaration_encoding(data, size, enc, len)`; the digest hashes the returned bool and, when true, the offset and length of the encoding name.
