You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `fixed_handler::on_digit(digit, divisor, remainder, error, exp, integral)`

## 1. Component overview

`fixed_handler` receives the decimal digits of a floating-point number one by one from the Grisu digit generator, when the caller asked for a fixed number of digits (`precision`). `on_digit` is called once per generated digit. It appends the digit to the output buffer and decides whether the generator should keep going, whether the requested precision has been reached (in which case the last digit is rounded using the remaining fraction), or whether the fast algorithm cannot decide and the caller has to use a slower fallback.

## 2. Functional requirements

State read and written: `buf` (digit characters), `size` (digits stored), `precision` (digits wanted). Arguments: `digit` (ASCII `'0'..'9'`), `divisor` (the weight of one unit of the digit just produced, in the scaled arithmetic of the generator), `remainder` (what is left of the number below the digit just produced, `remainder < divisor`), `error` (the uncertainty of `remainder`, an absolute value in the same scale), the unused `int` argument, and `integral` (true while the digit comes from the integral part of the scaled number).

1. Store `digit` at `buf[size]` and increase `size` by one.
2. If the new `size` is still **less than** `precision`, return `digits::more` (nothing else happens).
3. Otherwise the requested number of digits has been reached (or exceeded) and rounding is decided:
   1. If `integral` is false and the error is too large to decide anything, that is `error >= divisor` or `error >= divisor - error`, return `digits::error` (the digit stays stored).  When `integral` is true no such check is made (there `error == 1` and `divisor > 2`).
   2. Determine the rounding direction with `get_round_direction(divisor, remainder, error)`.
   3. If the direction is not `up`: return `digits::done` when it is `down`, and `digits::error` when it is `unknown`.
   4. If the direction is `up`: round the digit string up. Increase the last stored digit by one; when a digit becomes greater than `'9'` it turns into `'0'` and one is added to the digit before it, repeatedly (a carry). If the carry goes beyond the first digit, the first digit becomes `'1'` and one extra `'0'` is appended (`size` grows by one), e.g. `999` becomes `1000`. Then return `digits::done`.
4. The function never changes `precision`, `exp10`, `fixed` or `buf` characters other than as described.

Examples (digits already stored before the call -> after, result):
- stored `12`, `precision` 5, digit `3` -> `123`, `more`.
- stored `12`, `precision` 3, digit `3`, remainder well below half of the divisor, small error -> `123`, `done`.
- stored `12`, `precision` 3, digit `3`, remainder well above half -> `124`, `done`.
- stored `99`, `precision` 3, digit `9`, round up -> `1000` (size 4), `done`.
- stored `19`, `precision` 3, digit `9`, round up -> `200`, `done`.
- remainder close to half of the divisor relative to the error (neither clearly down nor clearly up) -> `error`.

## 3. Input specification

- `digit`: one of `'0'`..`'9'`. `divisor > 0`, `remainder < divisor`. If `integral` is false then `error` may be anything below `divisor`; if it is true then `error == 1` and `divisor > 2`. `buf` has room for `size + 2` characters. `size >= 0`; `precision` may be smaller than or equal to the size after storing (e.g. 0).

## 4. Output specification

Returns a `digits::result` (`more`, `done`, `error`). Mutates `buf` and `size` as described.

## 5. Edge cases and constraints

- With `precision <= size + 1` before the call, rounding is always attempted.
- Rounding only touches the digits already stored; the carry never reads before `buf[0]`.
- A result of `error` does not undo the stored digit: `size` stays increased by one.
- The function must be allocation-free and cheap: it is called for every generated digit.

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format-inl.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** the member function is defined inside `struct fixed_handler`, shown below. The stub is one of its member functions (the surrounding struct and the sibling member `on_start` are not part of your answer).

## Types and helpers visible to the function

```
#define FMT_ASSERT(condition, message)   // assert-like macro

enum round_direction { unknown, up, down };

// Given the divisor (normally a power of 10), the remainder = v % divisor for some number v and the error, returns
// whether v should be rounded up, down, or whether the rounding direction can't be determined due to error.
// Requires remainder < divisor and error < divisor - error.
inline round_direction get_round_direction(uint64_t divisor, uint64_t remainder, uint64_t error);

namespace digits {
enum result {
  more,   // Generate more digits.
  done,   // Done generating digits.
  error   // Digit generation cancelled due to an error.
};
}
```

## The enclosing struct (fixed-precision digit handler used by the Grisu digit generator)

```
struct fixed_handler {
  char* buf;        // output buffer; the digits generated so far are buf[0 .. size-1] (ASCII '0'..'9'); it has room for one more character than the digits
  int size;         // number of digits stored so far
  int precision;    // number of digits wanted (after on_start has adjusted it)
  int exp10;        // decimal exponent adjustment (not used by on_digit)
  bool fixed;       // fixed-point format flag (not used by on_digit)

  digits::result on_start(uint64_t divisor, uint64_t remainder, uint64_t error, int& exp);   // sibling, not to be implemented

  digits::result on_digit(char digit, uint64_t divisor, uint64_t remainder,
                          uint64_t error, int, bool integral);   // <-- the stub
};
```

## Caller (for orientation only)

```
// grisu_gen_digits(): after producing each next decimal digit it calls
//   result = handler.on_digit('0' + digit, power_of_10 << -one.e, remainder, error, exp, integral_part_flag);
//   if (result != digits::more) return result;
```

=== STUB ===
```cpp
digits::result on_digit(char digit, uint64_t divisor, uint64_t remainder,
                        uint64_t error, int, bool integral) {
    // TODO: implement according to the specification
}
```
