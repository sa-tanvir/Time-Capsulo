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
