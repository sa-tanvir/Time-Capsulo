You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `parse_arg_id(begin, end, handler)`

## 1. Component overview

Part of the format-string parser of the fmt library. It parses the *argument id* that follows the `{` of a replacement field: nothing (automatic numbering), a decimal index (`{0}`, `{12:x}`) or an identifier naming an argument (`{name}`, `{width:>5}`). The result is reported to a handler through callbacks and the function returns the position after the id.

## 2. Functional requirements

The range `[begin, end)` is the text that follows the opening brace; it is never empty. Let `c` be its first character.

1. **No id.** If `c` is `}` or `:`, call `handler()` (the call with no arguments) and return `begin` (nothing is consumed).
2. **Numeric id.** If `c` is a decimal digit, parse an index from the digits with `parse_nonnegative_int` (a leading `0` is a whole number by itself, so `0` is index 0 and in `01` only the `0` is the number). Number-too-big errors are reported by that helper to the handler's `on_error`. Afterwards:
   - if the number is followed by the end of the range, or by a character that is neither `}` nor `:`, call `handler.on_error("invalid format string")`;
   - otherwise call `handler(index)` with the parsed `int`.
   In both cases return the position directly after the digits (the position of the `}` or `:`, or of the offending character).
3. **Named id.** If `c` is a letter (`a`-`z`, `A`-`Z`) or `_`, the name is the longest prefix made of letters, digits and `_`. Call `handler(basic_string_view<Char>(begin, length))` with exactly that prefix and return the position after the name. No check is made on what follows the name (it may be the end of the range).
4. **Anything else** (any other first character, e.g. `-`, a space, `{`, a non-ASCII character): call `handler.on_error("invalid format string")` and return `begin`.

Exactly one handler call is made, except that a number that is too big first triggers `on_error("number is too big")` from the helper (which does not return in practice).

## 3. Input specification

- `begin`, `end`: `const Char*` with `begin != end`.
- `handler`: as described in the context. `on_error` is assumed not to return (it throws); behaviour after it returns is not tested.

## 4. Output specification

Returns the pointer to the first character after the parsed id, as described above. The function itself throws nothing; errors go through `handler.on_error`.

## 5. Edge cases and constraints

| text | handler call | returned offset |
|---|---|---|
| `}` , `:x` | `handler()` | 0 |
| `0}` | `handler(0)` | 1 |
| `12:>5` | `handler(12)` | 2 |
| `2147483647}` | `handler(2147483647)` | 10 |
| `2147483648}` | `on_error("number is too big")` | |
| `01}` | `on_error("invalid format string")` | 1 |
| `5x}` | `on_error("invalid format string")` | 1 |
| `7` | `on_error("invalid format string")` | 1 |
| `name}` | `handler("name")` | 4 |
| `_a1:x` | `handler("_a1")` | 3 |
| `abc` | `handler("abc")` | 3 |
| `9a}` | `on_error("invalid format string")` | 1 |
| `-1}` , ` }` , `{}` | `on_error("invalid format string")` | 0 |

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`

## Declaration line preceding the stub

The following line stands directly above the stub in the source file and is NOT part of your answer (do not repeat it):

```
template <typename Char, typename IDHandler>
```

`FMT_CONSTEXPR` is a macro for `constexpr` (C++14 and later) or nothing (C++11); keep it as in the stub.

## Helpers the function can use (same namespace)

```
#define FMT_ASSERT(condition, message)   // assert-like macro

template <typename Char> FMT_CONSTEXPR bool is_name_start(Char c);
    // true for 'a'..'z', 'A'..'Z' and '_'

template <typename Char, typename ErrorHandler>
FMT_CONSTEXPR int parse_nonnegative_int(const Char*& begin, const Char* end, ErrorHandler&& eh);
    // Precondition: begin != end and *begin is a digit. Parses a decimal unsigned integer and advances `begin` past it:
    // a leading '0' is a complete number by itself (exactly one character consumed, value 0); otherwise all consecutive
    // digits are consumed. If the value exceeds INT_MAX it calls eh.on_error("number is too big") (and, should that
    // return, yields an unspecified value). Otherwise returns the value.

template <typename Char> class basic_string_view;   // constructible as basic_string_view<Char>(const Char* data, size_t size)
```

## The IDHandler concept

`IDHandler` is a user supplied type; the argument is a forwarding reference. It provides

```
void operator()();                                // automatic indexing: no id given
void operator()(int index);                       // numeric id
void operator()(basic_string_view<Char> name);    // named id
void on_error(const char* message);               // reports an error; normally throws and does not return
```

## Caller (for orientation only)

```
// inside parse_format_string(): after '{', begin = parse_arg_id(begin, end, id_adapter{handler, 0}); // then expects '}' or ':'
```

=== STUB ===
```cpp
FMT_CONSTEXPR const Char* parse_arg_id(const Char* begin, const Char* end,
                                       IDHandler&& handler) {
    // TODO: implement according to the specification
}
```
