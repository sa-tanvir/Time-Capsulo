You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `utf8_decoder::process(data, size, result, Traits)`

## 1. Component overview

Part of pugixml's Unicode conversion layer (`namespace pugi::impl`, anonymous namespace in `src/pugixml.cpp`).
`utf8_decoder` is a stateless "decoder" policy: its static member template `process` walks a UTF-8 byte sequence, decodes
it into code points, and hands every decoded code point to an "encoder" policy (the `Traits` argument). Depending on the
policy, the same decoder is used to count the output size, to write UTF-16, UTF-32, UTF-8 or Latin-1 output, or to convert
to `wchar_t`. The decoder is lenient: it never fails, it silently drops bytes that cannot start or complete a sequence.

## 2. Functional requirements

Process `data[0 .. size)` from the front, one step at a time. At every step look at the lead byte `lead = data[i]`:

1. `lead < 0x80` (`0xxxxxxx`): code point `lead`; consumes 1 byte; reported through `Traits::low`.
2. `lead` in `0xC0..0xDF` (`110xxxxx`), **and** at least 2 bytes remain **and** the next byte is a continuation byte
   (`10xxxxxx`, i.e. `(b & 0xC0) == 0x80`): code point `((lead & 0x1F) << 6) | (b1 & 0x3F)`; consumes 2 bytes; `Traits::low`.
3. `lead` in `0xE0..0xEF` (`1110xxxx`), at least 3 bytes remain and the next two bytes are continuation bytes: code point
   `((lead & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F)`; consumes 3 bytes; `Traits::low`.
4. `lead` in `0xF0..0xF7` (`11110xxx`), at least 4 bytes remain and the next three bytes are continuation bytes: code
   point `((lead & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F)`; consumes 4 bytes; reported
   through `Traits::high` (not `low`).
5. In every other case (a stray continuation byte `0x80..0xBF`, a lead byte `0xF8..0xFF`, or a lead byte whose required
   continuation bytes are missing, either because the input ends or because a following byte is not a continuation byte)
   the single byte at the current position is **dropped**: nothing is reported, exactly 1 byte is consumed, and decoding
   continues with the next byte (which is examined afresh, so a truncated sequence can still be followed by a valid one).

There is deliberately **no further validation**: overlong encodings (leads `0xC0`, `0xC1`, `0xE0 0x80 0x80`, ...), surrogate
code points (`U+D800..U+DFFF` encoded as 3 bytes) and values above `U+10FFFF` (leads `0xF4..0xF7`) are decoded by the formulas
above and passed on as they are. A `0x00` byte inside the input is an ordinary code point 0 (the input is not NUL-terminated
in a way that matters; `size` governs).

## 3. Input specification

- `data`: `const uint8_t*`, `size` readable bytes (may be 0; the pointer may be unaligned; it may be anything, including
  not 4-byte aligned). Bytes at or after `data + size` must not be interpreted.
- `size`: `size_t`, number of bytes (up to several megabytes).
- `result`: `typename Traits::value_type`, the initial accumulator (an output pointer for writer policies, a count for counters).
- `Traits`: a policy type, passed by value only to deduce the template argument (its value is unused). It provides
  `typedef ... value_type;` plus two static functions (see context): `value_type low(value_type result, uint32_t ch)` for
  code points up to `0xFFFF` produced by rules 1-3, and `value_type high(value_type result, uint32_t ch)` for rule 4
  (`ch` up to `0x1FFFFF`).

## 4. Output specification

Returns the final accumulator value: starting from `result`, apply `result = Traits::low(result, cp)` or
`result = Traits::high(result, cp)` once for every decoded code point, in input order, and return the last `result`
(`result` itself if nothing was decoded). `process` must call the `Traits` functions exactly once per decoded code point,
in order, because writer policies write through the returned pointers. It writes nothing itself.

## 5. Edge cases and constraints

- `size == 0` -> returns `result` unchanged.
- `"a\xB0"` -> only `a` is reported; `"a\xB0_"` -> `a`, `_`; `"a\xC0"`, `"a\xD0_"` -> `a`, `_` (leads without continuation dropped);
  `"a\xE2\x80"` and `"a\xE2"` -> `a` only (truncated 3-byte); `"a\xF0\x90\x80"` -> `a` only.
- `"\xF2\x97\x98\xA4 \xF4\x80\x8F\xBF"` -> `high(0x97624)`, `low(0x20)`, `high(0x1003FF)`.
- `"\xC3\xA9"` -> `low(0xE9)`; `"\xE2\x82\xAC"` -> `low(0x20AC)`; `"\xC0\xAF"` -> `low(0x2F)` (overlong accepted).
- `"\xE2\x28\xA1"` -> drops `E2`, reports `(`, drops `A1`. `"\x82\x82\x82"` (any number of stray continuation bytes) -> nothing reported.
- Long inputs (megabytes) mostly made of ASCII must be processed quickly: runs of ASCII bytes are by far the most common
  input, and the function is on the hot path of every document load with a non-UTF-8 target encoding. The result must
  be independent of the input pointer's alignment.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++ (C++11, GCC 9)
- **File:** `src/pugixml.cpp`, inside `namespace pugi { namespace impl { namespace { ... } } }`
- **Enclosing scope:** the body of `struct utf8_decoder { typedef uint8_t type; ... };` (a struct with only static members; `process` is its only function)

## Includes available in this file

```
#include "pugixml.hpp"
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
#include <stdint.h>
```

Do not add includes or helper functions.

## Instance state

None: `utf8_decoder` has no data members; `process` is a static member function template and the `Traits` object argument is only used for template argument deduction.

## The `Traits` policies (existing code; `process` is instantiated with all of these)

```
struct utf16_counter { typedef size_t value_type;   // counts UTF-16 code units
    static value_type low(value_type result, uint32_t) { return result + 1; }
    static value_type high(value_type result, uint32_t) { return result + 2; } };

struct utf16_writer { typedef uint16_t* value_type;  // writes UTF-16 code units, returns pointer past them
    static value_type low(value_type result, uint32_t ch);    // *result = ch; return result + 1
    static value_type high(value_type result, uint32_t ch);   // writes a surrogate pair, returns result + 2
};

struct utf32_writer  { typedef uint32_t* value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // one uint32_t per call
struct latin1_writer { typedef uint8_t*  value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // one byte per call ('?' if not representable)
struct utf8_writer   { typedef uint8_t*  value_type; static value_type low(value_type, uint32_t ch); static value_type high(value_type, uint32_t ch); };  // re-encodes as UTF-8
struct utf8_counter, utf32_counter;                                           // size_t counters
```

The call site in the library (for orientation): `utf8_decoder::process(data, size, dest, utf16_writer())`.

=== STUB ===
```cpp
template <typename Traits> static inline typename Traits::value_type process(const uint8_t* data, size_t size, typename Traits::value_type result, Traits)
{
    // TODO: implement according to the specification
}
```
