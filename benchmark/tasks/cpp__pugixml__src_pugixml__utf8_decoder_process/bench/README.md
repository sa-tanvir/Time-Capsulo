Workload: UTF-8 byte strings decoded with several output policies. S holds hand-written strings (ASCII, 2/3/4-byte sequences, boundary
code points, surrogate encodings) and many malformed byte strings (stray continuation bytes, truncated sequences, overlong leads, 0xF8+ bytes);
M/L add `G` lines that `driver.cpp` expands deterministically (splitmix64) into tens of KB to ~3 MB of text with a chosen ASCII share and damage rate,
at 0-3 bytes of misalignment. The seven policy types are the library's own `utf16_writer`, `utf32_writer`, `latin1_writer`, `utf8_writer` and the
`utf16_counter`, `utf32_counter`, `utf8_counter`.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified) and calls
`pugi::impl::utf8_decoder::process(data, size, initial_result, Traits())`; the digest hashes the returned count and all written units.
The output area is reallocated outside the timed region.
