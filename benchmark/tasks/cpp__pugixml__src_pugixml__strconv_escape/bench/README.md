Workload: XML text containing character and entity references. S has the literal cases of the escape tests (valid and truncated
`&amp;`-style entities, decimal/hex numeric references of 1-4 byte code points, near-misses such as `&#1&#32;`, `&#x;`, `&a`);
M/L add `G` lines that `driver.cpp` expands deterministically (splitmix64) into thousands to hundreds of thousands of tokens
(plain characters, named/decimal/hex references, a percentage of malformed ones).
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified).
It copies the text into a fresh mutable buffer (outside the timed region), then walks it as the pcdata parser does: every `&` is passed to
`pugi::impl::strconv_escape(s, gap)`, and the gap is flushed at the end. The digest hashes the final text and the number of bytes consumed per call.
