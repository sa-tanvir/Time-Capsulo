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
