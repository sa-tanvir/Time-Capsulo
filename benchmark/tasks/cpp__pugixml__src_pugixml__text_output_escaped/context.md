# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level, defined after `class xml_buffered_writer`

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

## Types, constants and macros the function can use

```
typedef char char_t;                       // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN                           // function linkage macro; keep it as in the stub

enum chartypex_t { ctx_special_pcdata = 1, ctx_special_attr = 2, ctx_start_symbol = 4, ctx_digit = 8, ctx_symbol = 16 };
#define PUGI__IS_CHARTYPEX(c, ct)          // non-zero if character c has class bit ct in a 256-entry lookup table;
                                           // for ct == ctx_special_pcdata: control chars 0..31 except \t \r \n, '&', '<', '>' (and NUL)
                                           // for ct == ctx_special_attr:   control chars 0..31, '&', '<', '"', '\'' (and NUL)
                                           // false for every byte >= 0x80 and for every other character

// public format flags (pugixml.hpp)
const unsigned int format_no_escapes = 0x10;
const unsigned int format_skip_control_chars = 0x100;
const unsigned int format_attribute_single_quote = 0x200;
```

## `xml_buffered_writer` (existing class; non-copyable, buffer capacity is a few thousand characters)

```
class xml_buffered_writer
{
public:
    xml_buffered_writer(xml_writer& writer, xml_encoding user_encoding);
    size_t flush();                                    // pushes the buffered characters to the underlying xml_writer
    void write_direct(const char_t* data, size_t length);   // flushes the buffer, then writes `length` characters directly (large chunks)
    void write_buffer(const char_t* data, size_t length);   // appends `length` characters (any length; large chunks bypass the buffer)
    void write_string(const char_t* data);                  // appends a NUL-terminated string
    void write(char_t d0);                                  // append 1 character
    void write(char_t d0, char_t d1);                       // append 2 characters
    void write(char_t d0, char_t d1, char_t d2);            // ... up to 6 characters at once:
    void write(char_t d0, char_t d1, char_t d2, char_t d3);
    void write(char_t d0, char_t d1, char_t d2, char_t d3, char_t d4);
    void write(char_t d0, char_t d1, char_t d2, char_t d3, char_t d4, char_t d5);
};
```

## Sibling functions (for orientation)

```
PUGI__FN void text_output(xml_buffered_writer& writer, const char_t* s, chartypex_t type, unsigned int flags);
    // calls writer.write_string(s) if (flags & format_no_escapes), otherwise text_output_escaped(writer, s, type, flags)
// it is called with ctx_special_pcdata for element text and with ctx_special_attr for attribute values
```
