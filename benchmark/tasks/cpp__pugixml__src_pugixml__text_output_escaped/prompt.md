You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `text_output_escaped(writer, s, type, flags)`

## 1. Component overview

Part of pugixml's XML serializer (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). When a document
is saved, the text of an element (`node_pcdata`) and the value of an attribute must be written with the characters that are
special in XML replaced by entity references or numeric character references. `text_output_escaped` does this for one
NUL-terminated string and sends the result to an `xml_buffered_writer` (a buffering front end to the user's output stream).
The same function is used for element text and for attribute values; the `type` argument tells which set of characters is special.

## 2. Functional requirements

Walk the string `s` from the start up to (not including) its terminating NUL, and write to `writer`, in order:

1. Characters that are **not special** for `type` are copied unchanged. All bytes `>= 0x80` (multi-byte UTF-8 sequences) are
   never special and are copied unchanged.
2. Which characters are special depends on `type`:
   - `ctx_special_pcdata` (element text): `&`, `<`, `>` and the control characters `0x01..0x1F` **except** tab (`0x09`),
     line feed (`0x0A`) and carriage return (`0x0D`). `"` and `'` are *not* special here and are copied.
   - `ctx_special_attr` (attribute value): `&`, `<`, `"`, `'` and **all** control characters `0x01..0x1F` (including tab,
     line feed and carriage return). `>` is *not* special here and is copied.
   (The library has a lookup table for this: `PUGI__IS_CHARTYPEX(c, type)` is true exactly for the special characters of `type`.)
3. A special character is written as:
   - `&` -> `&amp;`
   - `<` -> `&lt;`
   - `>` -> `&gt;`
   - `"` -> `&quot;`, but if `flags & format_attribute_single_quote` the `"` is written as is (it is the attribute value in
     single quotes that needs escaping then);
   - `'` -> written as is, but if `flags & format_attribute_single_quote` it is written as `&apos;`;
   - a control character with code `c` (1..31) -> a numeric reference with **exactly two decimal digits**:
     `&#` + tens digit + units digit + `;`, e.g. `&#04;`, `&#09;`, `&#10;`, `&#13;`, `&#31;`. If
     `flags & format_skip_control_chars` such a character is dropped and nothing is written for it.
4. The terminating NUL ends the text; it is not written. An empty string writes nothing.
5. Nothing is returned; all output goes through `writer` (it is **not** flushed by this function).

## 3. Input specification

- `writer`: `xml_buffered_writer&`, an initialized buffering writer (see context for its public methods). Calls to its
  methods append characters to the output; it flushes itself when its internal buffer fills up. It may already contain
  pending data from earlier calls; the output of this function must follow it.
- `s`: `const char_t*` (`char`), NUL-terminated, never null. May be megabytes long, may contain any bytes (control
  characters `0x01..0x1F` are possible; the byte `0x7F` is not special).
- `type`: `chartypex_t`, either `ctx_special_pcdata` or `ctx_special_attr`.
- `flags`: `unsigned int`, a combination of the `format_*` constants; only `format_skip_control_chars` (0x100) and
  `format_attribute_single_quote` (0x200) matter here.

## 4. Output specification

The escaped text appended to `writer`'s output, as defined above. No return value, no exceptions.

## 5. Edge cases and constraints

- Element text `<>'"&\x04\r\n\t` -> `&lt;&gt;'"&amp;&#04;` followed by the raw bytes `\r`, `\n`, `\t`.
- Attribute value `<>'"&\x04\r\n\t` -> `&lt;>'&quot;&amp;&#04;&#13;&#10;&#09;`; with `format_attribute_single_quote`:
  `&lt;>&apos;"&amp;&#04;&#13;&#10;&#09;`.
- With `format_skip_control_chars`, element text `a\x01b\tc` -> the byte sequence `a`, `b`, TAB, `c` (the control character `\x01` is dropped; the tab is not special for element text);
  for an attribute value the tab is special too and is dropped as well, giving `abc`.
- Already-escaped input is escaped again: `&amp;` -> `&amp;amp;`.
- Plain text should be copied in chunks, not character by character through the writer's per-character methods: documents
  with megabytes of unescaped text are normal, and the function must stay linear with a small constant.

=== CONTEXT ===
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

=== STUB ===
```cpp
PUGI__FN void text_output_escaped(xml_buffered_writer& writer, const char_t* s, chartypex_t type, unsigned int flags)
{
    // TODO: implement according to the specification
}
```
