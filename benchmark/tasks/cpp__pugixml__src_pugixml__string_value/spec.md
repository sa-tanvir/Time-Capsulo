# Functional specification: `string_value(na, alloc)`

## 1. Component overview

Part of pugixml's XPath engine (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). It computes the
XPath **string-value** of a node or attribute (XPath 1.0, section 5): what `string()`, `string(node-set)`, comparisons of a node-set
with a string or number, `sum()`, `normalize-space()` and similar functions use as the text of a node. The result is an
`xpath_string` (the engine's string type, see context); strings that must be built (concatenations) take their memory from the
engine's `xpath_allocator` `alloc`.

## 2. Functional requirements

`na` is an `xpath_node`: it holds either an attribute (with its parent element) or a DOM node, or nothing.

1. **Attribute.** If `na.attribute()` is non-null, the result is the attribute's value text (`attribute().value()`), regardless of the
   parent. No copy is required.
2. **Text-like nodes.** If `na.node()` is of type `node_pcdata`, `node_cdata`, `node_comment` or `node_pi`, the result is that node's
   value: the character data, the CDATA content, the comment text, or the processing-instruction data (the part after the target;
   not the target name).
3. **Element and document nodes** (`node_element`, `node_document`): the result is the concatenation, in document order, of
   - the node's **own value** first, if it has a non-empty one (an element has a value only when the document was parsed with
     `parse_embed_pcdata`, which stores a leading text child inside the element instead of creating a `node_pcdata` child), then
   - the values of **all descendant** `node_pcdata` and `node_cdata` nodes, at any depth, in document order.
   Descendant comments, processing instructions, declarations, doctype nodes, attributes and element names contribute nothing.
   Only the *starting* node's own value is used: the own value stored in a descendant **element** (again only possible with
   `parse_embed_pcdata`) is **not** included.
4. **Any other node** (`node_declaration`, `node_doctype`, a null node, i.e. `na` holding nothing): the empty string.
5. Empty text nodes contribute nothing (the string-value of `head`, ``, `tail` pcdata siblings under a document is `headtail`).
6. Concatenation is done through `xpath_string::append(other, alloc)`. If memory for a concatenation cannot be obtained from `alloc`,
   `append` leaves its target unchanged, and the string-value is then simply missing that text; this is not an error and nothing is thrown.

## 3. Input specification

- `na`: `const xpath_node&`. Attribute case: `na.attribute()` valid and `na.parent()` its element. Node case: `na.node()`
  valid (possibly the document node) or invalid (empty `xpath_node`).
- `alloc`: `xpath_allocator*`, never null. Documents may be large (hundreds of thousands of nodes) and deeply nested, so the traversal of the
  subtree must not use recursion proportional to the nesting depth.

## 4. Output specification

An `xpath_string` with the text defined above. For an attribute or a text-like node it may refer directly to the stored value; for elements
and documents it is the concatenation (a constant string if only one piece has to be returned is fine, a heap string otherwise).

## 5. Edge cases and constraints

Document `<node><c1>pcdata</c1><c2><child/></c2><c3 attr='avalue'/><c4><?target pivalue?></c4><c5><!--comment--></c5><c6><![CDATA[cdata]]></c6></node>`
(parsed with comments and processing instructions kept):

| `na` | result |
|---|---|
| document node, or `node` | `pcdatacdata` |
| first child of `c1` (pcdata) | `pcdata` |
| first child of `c2` (the `child` element) | the empty string |
| attribute `attr` of `c3` | `avalue` |
| first child of `c4` (PI) | `pivalue` |
| first child of `c5` (comment) | `comment` |
| first child of `c6` (CDATA) | `cdata` |
| empty `xpath_node` | the empty string |

Parsed with `parse_embed_pcdata`, `<a>x<b>y</b>z</a>` gives an element `a` whose own value is `x`, a child element `b` whose own value is `y`, and a
`node_pcdata` child `z` of `a`. The string-value of `a` is `xz` (own value, then the pcdata child; `b`'s embedded `y` is not included);
the string-value of `b` is `y`; the string-value of the document node is `z` (the document has no own value, and `a`'s embedded `x`
is not included either). `<a>x</a>` parsed the same way has no children at all and the string-value of `a` is `x`.
Adjacent text pieces are concatenated without separators. The function is called for every node of a node-set in comparisons, so
nodes with a single text child should not need a copy.
