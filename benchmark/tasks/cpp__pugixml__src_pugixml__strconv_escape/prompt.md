You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `strconv_escape(char_t* s, gap& g)`

## 1. Component overview

Part of pugixml's parser (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`). When the parser runs with
entity conversion enabled (`parse_escapes`) and meets an `&` in character data or an attribute value, it calls
`strconv_escape` to decode **one** reference in place. The decoded characters are written over the start of the reference
inside the same mutable text buffer; the now-unused remainder of the reference is recorded as a "gap" so that the parser
can later close it up lazily. The function returns the position where the parser must continue scanning.

## 2. Functional requirements

`s` points at an `&` character. Let the text after it be examined as follows (the characters are case-sensitive):

1. **Numeric references.** `&#` followed by decimal digits `0-9` and a terminating `;`, or `&#x` (lowercase `x` only)
   followed by hexadecimal digits `0-9`, `a-f`, `A-F` and a terminating `;`. The number is accumulated in an
   `unsigned int` (arithmetic wraps modulo 2^32 for very long digit strings). Its replacement is the UTF-8 encoding of that
   code point (1 to 4 bytes: below 0x80 one byte, below 0x800 two, below 0x10000 three, otherwise four, with no further
   validation of the value) and is written starting at `s`. The existing helper `utf8_writer::any(uint8_t* dst, uint32_t ch)`
   writes exactly this encoding and returns the pointer past it.
2. **Named references**, exact spelling including the `;`: `&amp;` -> `&`, `&lt;` -> `<`, `&gt;` -> `>`, `&quot;` -> `"`,
   `&apos;` -> `'`. The single replacement character is written at `s`.
3. **Success.** After writing the replacement, let `p` be the position just after the written bytes and `end` the position just
   after the reference's `;`. The leftover bytes `[p, end)` are registered as a gap by calling `g.push(p, end - p)` (the
   existing `gap::push(char_t*&, size_t)`, see context; `p` is passed as a local variable that `push` advances).
   The function returns `end`.
4. **Anything else is not a valid reference** (unknown names, `&;`, missing `;`, empty number `&#;` or `&#x;`, a non-digit
   inside a number, uppercase `&#X..`, a sign as in `&#-;`, and the end of the string inside a reference). Then the
   buffer and `g` are left untouched and the function returns the position of the first character that did not fit the
   expected pattern (it is not consumed), so that the caller resumes scanning exactly there. That position is:
   - for `&#` / `&#x` followed by digits: the first non-digit character (for `&#;` and `&#x;` that is the `;` itself; for
     `&#1&#32;` it is the second `&`; for `&#X41;` it is the `X`);
   - for `&a`: if the next character is `m`, it checks for `p;` after it, else if it is `p` it checks for `os;` after it; the
     returned position is the first character that deviates (e.g. for `&am;` the `;` , for `&amp` the terminating NUL,
     for `&a<` the `<`);
   - for `&g`, `&l`, `&q`: the first character deviating from `t;`, `t;` and `uot;` respectively;
   - for any other character after the `&` (including `&&`, `&;`, a NUL after the `&`): `s + 1`.

   In every failing case the returned position is at most the NUL terminator: the function never reads beyond it.

## 3. Input specification

- `s`: `char_t*` (here `char`), pointing at an `&` inside a mutable NUL-terminated buffer; the bytes from `s` up to the
  terminator may be read, and the reference may be rewritten (successful decodes only ever write at most as many bytes as
  the reference occupies).
- `g`: a `gap` object (default state: `end == 0`, `size == 0`), shared across calls on the same buffer. It is only
  modified through `g.push` on success.

## 4. Output specification

Returns the `char_t*` described above (just after the `;` on success, the failure position otherwise). Side effects on
success: replacement bytes written at `s`, a gap registered through `g.push`. No side effect on failure. The caller later calls
`g.flush` to compact the buffer, so after flushing, each decoded reference must appear exactly once as its replacement
and all other text unchanged.

## 5. Edge cases and constraints

- `"&amp;"` -> writes `&`, returns `s + 5`; `"&#65;"` -> writes `A`, returns `s + 5`; `"&#x24B62;"` -> writes the 4 bytes
  `F0 A4 AD A2`, returns `s + 9`; `"&#x03B3;"` and `"&#x03b3;"` -> the 2 bytes `CE B3`.
- `"&#1&#32;"` -> nothing written, returns `s + 3` (pointing at the second `&`); `"&#x1-"` -> returns `s + 4`;
  `"&quot"` (end of string) -> returns pointer to the NUL; `"&#;"`, `"&#x;"`, `"&;"` -> returns `s + 2`, `s + 3`, `s + 1`.
- `"&#/;"`, `"&#:;"`, `"&#a;"`, `"&#A;"`, `"&#XA;"` and `"&#xG;"`, `"&#x`;"`, `"&#x@;"` are all invalid; `"&#01;"` and
  `"&#x01;"` are valid (leading zeros allowed, value 1).
- Digit strings of any length are accepted (leading zeros, values above 0x10FFFF, wrapping past 2^32).
- Per call the work is proportional to the length of the reference; the parser calls this function once per `&`, up to
  hundreds of thousands of times per document.

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

## Types and helpers the function can use

```
typedef char char_t;      // character type (this build is not PUGIXML_WCHAR_MODE)
#define PUGI__FN          // function linkage macro; keep it as in the stub

// Gap bookkeeping used by the parser to collapse decoded entities lazily (existing code, do not modify)
struct gap
{
    char_t* end;     // 0 when there is no gap yet; otherwise the end of the most recently pushed gap
    size_t size;     // total number of bytes in all gaps pushed so far

    gap(): end(0), size(0) {}

    // Push a new gap of `count` bytes starting at s: collapses the previous gap (moves the text between the end
    // of the previous gap and s back over it), then advances s by count, and remembers the new gap end = s.
    void push(char_t*& s, size_t count);

    // Collapses the last gap and returns the new past-the-end pointer of the text
    char_t* flush(char_t* s);
};

struct utf8_writer
{
    typedef uint8_t* value_type;
    // Writes the UTF-8 encoding of ch (1 byte below 0x80, 2 below 0x800, 3 below 0x10000, otherwise 4) at result
    // and returns the pointer past the written bytes.
    static value_type any(value_type result, uint32_t ch);
};
```

## How the function is called (for orientation only)

```
// inside the pcdata / attribute parsers, with `gap g;` declared by the caller:
if (*s == '&') s = strconv_escape(s, g);   // otherwise ++s
...
end = g.flush(s);                          // at the end of the text
```

=== STUB ===
```cpp
PUGI__FN char_t* strconv_escape(char_t* s, gap& g)
{
    // TODO: implement according to the specification
}
```
