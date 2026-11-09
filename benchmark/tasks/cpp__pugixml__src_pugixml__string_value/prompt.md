You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, in the XPath implementation section

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
```

Do not add includes or helper functions.

## Types and helpers the function can use

```
typedef char char_t;                       // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN                           // function linkage macro; keep it as in the stub

struct xpath_allocator;                    // memory arena used for evaluation results (opaque here, passed on to xpath_string::append)

class xpath_string                         // value type; cheap to copy; does not own constant strings
{
public:
    xpath_string();                                                         // the empty string
    static xpath_string from_const(const char_t* str);                      // refers to a NUL-terminated constant string (not copied)
    void append(const xpath_string& o, xpath_allocator* alloc);             // appends o; copies into allocator memory when needed;
                                                                            // a no-op if o is empty; leaves *this unchanged when allocation fails
    const char_t* c_str() const;
    size_t length() const;
    bool empty() const;
};

// public DOM API (pugixml.hpp), all const and cheap
enum xml_node_type { node_null, node_document, node_element, node_pcdata, node_cdata, node_comment, node_pi, node_declaration, node_doctype };

class xml_node
{
public:
    xml_node_type type() const;
    const char_t* value() const;           // never null ("" when the node has no value)
    xml_node first_child() const;          // null node (converts to false) when there is none
    xml_node next_sibling() const;
    xml_node parent() const;
    bool operator==(const xml_node& r) const;
    bool operator!=(const xml_node& r) const;
    operator unspecified_bool_type() const;   // usable in conditions, false for the null node
};

class xml_attribute { public: const char_t* value() const; /* never null */ operator unspecified_bool_type() const; };

class xpath_node
{
public:
    xml_node node() const;                 // the node; null when the xpath_node holds an attribute or is empty
    xml_attribute attribute() const;       // the attribute; null when the xpath_node holds a node
    xml_node parent() const;
};
```

## Callers (for orientation only)

```
// xpath_ast_node::compare_eq / compare_rel / eval_string / eval_number ... all use it, e.g.:
//     if (comp(string_value(*li, stack.result), string_value(*ri, stack.result))) return true;
//     return convert_string_to_number(string_value(c.n, stack.result).c_str());
```

=== STUB ===
```cpp
PUGI__FN xpath_string string_value(const xpath_node& na, xpath_allocator* alloc)
{
    // TODO: implement according to the specification
}
```
