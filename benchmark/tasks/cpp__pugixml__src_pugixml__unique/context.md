# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, a function template. The file section it belongs to contains small generic algorithm helpers (`swap`, `min_element`, `reverse`, `sort`, `hash_insert`) used by the XPath code.

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

Do not add includes or helper functions. (`<algorithm>` is **not** available.)

## Helpers the function can use

```
#define PUGI__FN                           // function linkage macro; keep it as in the stub

template <typename T> inline void swap(T& lhs, T& rhs);            // exchanges two objects
template <typename I> PUGI__FN void reverse(I begin, I end);       // reverses a range in place
```

## Caller (for orientation only)

```
// in xpath_node_set_raw::remove_duplicates(xpath_allocator* alloc), for sorted node sets (xpath_node* _begin, _end):
_end = unique(_begin, _end);
```
