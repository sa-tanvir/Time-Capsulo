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
