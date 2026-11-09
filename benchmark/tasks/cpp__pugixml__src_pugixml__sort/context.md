# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, a function template. The file section it belongs to contains small generic algorithm helpers (`swap`, `min_element`, `reverse`, `unique`, `hash_insert`) used by the XPath code.

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

Do not add includes, helper functions or helper structs. (`<algorithm>` is **not** available.)

## Helpers the function can use

```
#define PUGI__FN                           // function linkage macro; keep it as in the stub

template <typename T> inline void swap(T& lhs, T& rhs)      // exchanges two objects through a temporary copy
{ T temp = lhs; lhs = rhs; rhs = temp; }

struct less        { template <typename T> bool operator()(const T& lhs, const T& rhs) const { return lhs < rhs; } };
struct document_order_comparator { bool operator()(const xpath_node& lhs, const xpath_node& rhs) const; };   // document order of two XPath nodes
```

## Caller (for orientation only)

```
// in xpath_sort(xpath_node* begin, xpath_node* end, xpath_node_set::type_t type, bool rev), for unsorted node sets:
sort(begin, end, document_order_comparator());     // begin/end are xpath_node*
```
