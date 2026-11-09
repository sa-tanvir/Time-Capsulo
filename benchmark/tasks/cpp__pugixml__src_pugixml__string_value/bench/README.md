Workload: XML documents plus a set of XPath nodes whose string value is requested. S holds small literal documents (nested text, CDATA, comments,
processing instructions, entities, declaration and doctype, namespaces), each parsed with and without `parse_embed_pcdata`; M/L add `G` lines that `driver.cpp`
expands deterministically (splitmix64) into documents of 2*10^4 to 4*10^5 items with chosen nesting depth.
Invocation: `driver.cpp` `#include`s `/w/src/pugixml.cpp` (compiled into `/build/drv`, cached by content hash, so `/w` is never modified). The documents are parsed and the
query nodes chosen before timing (the document node, a sample of descendants limited by a total-size budget, and the first attributes of sampled elements);
the timed region calls `pugi::impl::string_value(xpath_node, &alloc)` for each of them with a fresh `xpath_allocator`. The digest hashes every resulting string.
