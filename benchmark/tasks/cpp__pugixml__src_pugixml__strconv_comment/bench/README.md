Workload: comment bodies (the text after `<!--`) in mutable buffers. S holds literal cases (immediate terminator, `\r`, `\r\n` and `\r\r` line breaks, dashes that do not
terminate, missing terminators, the `endch` rule where a closing `>` has been replaced by the buffer's NUL); M/L add `G` lines that `driver.cpp` expands deterministically
(splitmix64) into 2*10^4 to 3*10^6 bytes with 0-20% line breaks, followed by a proper `-->` and trailing text, no terminator, or `--` + end of buffer.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified); a fresh mutable copy of the text is made
outside the timed region, then `pugi::impl::strconv_comment(buffer, endch)` is called. The digest hashes the returned offset (or null) and, on success, the comment text
that was compacted in place and NUL-terminated.
