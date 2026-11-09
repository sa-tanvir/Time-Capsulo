Workload: texts to be escaped for element content or attribute values. S holds literal cases (every special character, control characters,
already-escaped text, multibyte UTF-8) for both contexts and for the flag combinations none / `format_skip_control_chars` /
`format_attribute_single_quote`; M/L add `G` lines that `driver.cpp` expands deterministically (splitmix64): 2*10^4 to 4*10^6 bytes of plain runs
with 0-10% special characters and a few multibyte characters.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified), wraps a capturing `xml_writer`
in `xml_buffered_writer(writer, encoding_utf8)`, calls `pugi::impl::text_output_escaped(bw, text, type, flags)`, flushes, and the digest hashes the captured bytes.
