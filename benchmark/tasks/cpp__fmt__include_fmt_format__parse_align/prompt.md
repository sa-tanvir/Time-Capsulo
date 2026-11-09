You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `parse_align(begin, end, handler)`

## 1. Component overview

Part of the format-string parser of the fmt library. It parses the optional `[[fill]align]` prefix of a standard format specification (for example the `*^` of `{:*^10}` or the `>` of `{:>5}`). It reports what it found to a handler object through callbacks and returns the position after the part it consumed.

## 2. Functional requirements

The range `[begin, end)` is the text of the specification (it is never empty). An *alignment character* is one of `<` (left), `>` (right), `^` (center) and `=` (numeric); they map to `align::left`, `align::right`, `align::center` and `align::numeric` respectively.

1. If the range has at least two characters and the **second** character is an alignment character, the **first** character is a fill character (any character, including another alignment character). The function calls `handler.on_fill(first)` and then `handler.on_align(align)`, and consumes two characters.
2. Otherwise (the range has one character, or its second character is not an alignment character), if the **first** character is an alignment character, the function calls `handler.on_align(align)` once (no `on_fill`) and consumes one character.
3. Otherwise nothing is consumed and no callback is made.
4. Rule 1 has priority over rule 2: for `<<` the fill is `<` and the alignment is left; for `<>` the fill is `<` and the alignment is right; for `x<` the fill is `x`.
5. Exception to rule 1: the fill character `{` is not allowed. When rule 1 applies with first character `{` (for example `{<`, `{^`), the function calls `handler.on_error("invalid fill character '{'")` and returns `begin` (nothing consumed); neither `on_fill` nor `on_align` is called. If `on_error` returns normally, the function still returns `begin`. A lone `{` followed by a non-alignment character is not an error: rule 3 applies. A leading `{` is fine when it is the only alignment-relevant character, e.g. for `{` alone nothing happens.
6. Only the first two characters are ever inspected; the remaining text (width, precision, type, ...) is left untouched.
7. When the character type is wider than `char`, characters are compared to the alignment characters after conversion to `char` (truncation).

## 3. Input specification

- `begin`, `end`: pointers to `Char` with `begin != end` (at least one character).
- `handler`: object with `on_fill`, `on_align` and `on_error` as described in the context.

## 4. Output specification

Returns the pointer to the first character not consumed: `begin`, `begin + 1` or `begin + 2`. Callbacks are made in the order `on_fill` then `on_align`, at most once each. No exceptions are thrown by the function itself (the handler's `on_error` may throw).

## 5. Edge cases and constraints

| text | callbacks | returned offset |
|---|---|---|
| `<` | `on_align(left)` | 1 |
| `*^` | `on_fill('*')`, `on_align(center)` | 2 |
| `*^7` | `on_fill('*')`, `on_align(center)` | 2 |
| `<<` | `on_fill('<')`, `on_align(left)` | 2 |
| `x<y` | `on_fill('x')`, `on_align(left)` | 2 |
| `<x` | `on_align(left)` | 1 |
| `=5` | `on_align(numeric)` | 1 |
| `ab` , `x` , `5` | none | 0 |
| `{<` | `on_error("invalid fill character '{'")` | 0 |
| `{` | none | 0 |

The function is called with every format specification parsed by the library, so it must be fast and must not allocate.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename Char, typename Handler>
```

`FMT_CONSTEXPR` is a macro for `constexpr` (C++14 and later) or nothing (C++11); keep it as in the stub.

## Types visible to the function

```
namespace align { enum type { none, left, right, center, numeric }; }
using align_t = align::type;
#define FMT_ASSERT(condition, message)   // assert-like macro
#define FMT_NUMERIC_ALIGN 1              // the '=' alignment is enabled in this build
```

`Handler` is a user supplied type with these member functions (the argument is a forwarding reference):

```
void on_fill(Char fill);       // reports the fill character
void on_align(align_t align);  // reports the alignment
void on_error(const char* message);   // may throw; if it returns, parsing continues
```

## Caller (for orientation only)

```
// in parse_format_specs(): it = parse_align(begin, end, handler);  // begin points just after the ':' of "{:...}"
```

=== STUB ===
```cpp
FMT_CONSTEXPR const Char* parse_align(const Char* begin, const Char* end,
                                      Handler&& handler) {
    // TODO: implement according to the specification
}
```
