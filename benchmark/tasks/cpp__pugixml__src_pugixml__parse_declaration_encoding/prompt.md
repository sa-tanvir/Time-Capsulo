You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `parse_declaration_encoding(data, size, out_encoding, out_length)`

## 1. Component overview

Part of pugixml's encoding auto-detection (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). When a
document buffer looks like it starts with an XML declaration (`<?xml ...?>`) in an ASCII-compatible encoding, the
detection code calls this function to find the value of the `encoding="..."` pseudo-attribute without parsing the
whole declaration. It only locates the name; it neither validates it nor maps it to an encoding.

## 2. Functional requirements

Work on the raw bytes `data[0 .. size)`; never read at or beyond `data + size`.

1. The buffer must begin with the five bytes `<?xml` followed by a whitespace byte (space, tab `\t`, line feed `\n`
   or carriage return `\r`). That needs `size >= 6`. If not, return `false`.
2. Scan from index 6 upwards (as long as at least two bytes remain at the current index, i.e. `i + 1 < size`), looking at each
   index `i` in turn:
   - if `data[i] == '?'` return `false` (the declaration ended without an encoding; a `?` is not allowed inside values);
   - if `data[i] == 'e'` and `data[i + 1] == 'n'` this is taken to be the start of the encoding attribute and the rest is
     decided there (the scan does **not** go on past this point; a mismatch below returns `false`):
     a. the eight bytes `encoding` must follow from `i` on;
     b. then zero or more whitespace bytes (space, `\t`, `\n`, `\r`), then `=`, then zero or more whitespace bytes;
     c. then a delimiter: `"` if the next byte is `"`, otherwise `'` is expected (so anything other than `"` or `'` fails);
        it is consumed;
     d. the value is the run of zero or more "symbol" bytes: ASCII letters, digits, `_`, `:`, `-`, `.`, and any byte
        `>= 0x80`. The name may be empty. Scanning stops at the first other byte;
     e. the same delimiter character must follow the value immediately, otherwise return `false`;
     f. on success set `out_encoding` to point at the first byte of the value (inside `data`) and `out_length` to its
        length in bytes, and return `true`. Nothing after the closing delimiter is looked at.
   - otherwise continue with `i + 1`.
3. If the scan finishes without finding a candidate (including when `size` is too small), return `false`.

When the function returns `false`, the contents of `out_encoding` and `out_length` are unspecified (callers must not use them).
Names and bytes are not case-folded: `ENCODING` or `<?XML` do not match.

## 3. Input specification

- `data`: `const uint8_t*`, at least `size` readable bytes (it need not be NUL-terminated).
- `size`: `size_t`, up to several megabytes (a declaration can be preceded by very long attribute lists).
- `out_encoding`: `const uint8_t*&`, output parameter. `out_length`: `size_t&`, output parameter.

## 4. Output specification

`bool`. `true` only when a well-formed `encoding` pseudo-attribute as described was found; then `out_encoding` points into `data`
at the value and `out_length` is the value length.

## 5. Edge cases and constraints

| buffer | result |
|---|---|
| `<?xml version='1.0' encoding='UTF-8'?>` | true, value `UTF-8` (length 5) |
| `<?xml encoding = 'ISO-8859-1' ?>` | true, `ISO-8859-1` |
| `<?xml\tencoding\t=\t"windows-1252"?>` | true, `windows-1252` |
| `<?xml version='1.0' encoding=''?>` | true, length 0 |
| `<?xml version='1.0'?>` | false (stops at `?`) |
| `<?xml version='1.0' encoding=utf-8?>`, `... encoding 'x'?>`, `... encoding='a b'?>` | false |
| `<?xml version='1.0' encoding='utf-8` (truncated) | false |
| `<?xml version='1.0' encoding='utf-8"?>` (mismatched quote) | false |
| `<?xml version='1.0' enable='1' encoding='utf-8'?>` | false (the first `en` is not `encoding`) |
| `<?xmlx encoding='a'?>`, `<?XML encoding='a'?>`, `<?xml` (size 5), size 0 | false |
| `<?xml encoding='a'` (size ends right after the closing quote) | true, `a` |

Long declarations (hundreds of thousands of bytes of other pseudo-attributes or whitespace before `encoding`) are scanned
in a single linear pass; running time must be linear in `size`.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }` (all helpers below are in the same namespace and visible)
- **Enclosing scope:** namespace level

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

## Types and macros the function can use

```
typedef char char_t;
#define PUGI__FN                           // function linkage macro; keep it as in the stub

enum chartype_t { ct_parse_pcdata = 1, ct_parse_attr = 2, ct_parse_attr_ws = 4, ct_space = 8, ct_parse_cdata = 16,
                  ct_parse_comment = 32, ct_symbol = 64, ct_start_symbol = 128 };
#define PUGI__IS_CHARTYPE(c, ct)           // non-zero if byte c belongs to class ct (table lookup, c is an unsigned byte value):
                                           //   ct_space:  ' ', '\t', '\n', '\r'
                                           //   ct_symbol: a-z, A-Z, 0-9, '_', ':', '-', '.', and every byte >= 0x80
```

## Caller (for orientation only)

```
// inside guess_buffer_encoding(const uint8_t* data, size_t size), when the buffer starts with the bytes "<?xm":
const uint8_t* enc = 0; size_t enc_length = 0;
if (parse_declaration_encoding(data, size, enc, enc_length)) { /* compare the name with "latin1", "iso-8859-1" (case-insensitive) */ }
```

=== STUB ===
```cpp
PUGI__FN bool parse_declaration_encoding(const uint8_t* data, size_t size, const uint8_t*& out_encoding, size_t& out_length)
{
    // TODO: implement according to the specification
}
```
