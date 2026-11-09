You are an expert C++ developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing C++ code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```cpp code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `float_writer<Char>::prettify(it)`

## 1. Component overview

`float_writer` turns a decimal digit string and an exponent (for example digits `12345` and exponent `-3`, i.e. 12.345) into the text of a floating-point number. `prettify` (a const member function) writes the number, without any sign, to an output iterator and returns the iterator advanced past the last character written. It supports the exponent notation (`1.2345e+01`) and the positional notation (`12.345`, `0.00012345`, `12340000`), with or without zero padding to the requested precision.

## 2. Functional requirements

Notation: `n = num_digits_`, `D = digits_[0..n-1]`, and `full_exp = n + exp_`, so that `10^(full_exp-1) <= value < 10^full_exp` when `D[0] != '0'`. `precision` and `trailing_zeros` are those of `specs_`. `point` is `decimal_point_`. `specs_.format` is either `exp` or something else (positional notation: `general` or `fixed`).

**A. Exponent notation (`specs_.format == exp`).** Write, in this order:
1. `D[0]`.
2. If `n > 1`: the decimal point character, then `D[1..n-1]`. (When `n == 1` no decimal point is written.)
3. If `trailing_zeros` is set and `precision - n > 0`: that many `'0'` characters.
4. `'E'` if `specs_.upper`, else `'e'`.
5. The exponent `full_exp - 1` as a sign (`+` or `-`) followed by its absolute value with at least two digits (`e+00`, `e-07`, `e+100`, `e-305`).

**B. Positional notation (any other format).** Three cases depending on `full_exp`:

1. *`n <= full_exp` (the value is an integer).* Write all `n` digits followed by `full_exp - n` zeros. Then, only if `trailing_zeros` is set: write the decimal point; let `z = precision - full_exp`; if `z <= 0`, write one `'0'` after the point unless the format is `fixed` (then nothing), and stop; otherwise write `z` zeros. Without `trailing_zeros` nothing follows (digits `1234`, exponent 7 give `12340000000`).
2. *`0 < full_exp < n` (digits on both sides of the point).* Write the first `full_exp` digits.
   - Without `trailing_zeros`: ignore trailing `'0'` digits of D after position `full_exp` (never cutting into the first `full_exp` digits). If at least one digit remains after the integer part, write the decimal point and the remaining digits; if none remain, write no point (`12.30` becomes `12.3`, `12.00` becomes `12`).
   - With `trailing_zeros`: write the decimal point and all remaining digits (including zeros of D); then, if `precision > n`, append `precision - n` zeros.
3. *`full_exp <= 0` (the value is below one).* Write `'0'`. Let `zeros = -full_exp`; if `precision >= 0` and `precision < zeros` then `zeros = precision`. Let `m = n`; without `trailing_zeros`, reduce `m` while `m > 0` and `D[m-1] == '0'`. If `zeros != 0` or `m != 0`: write the decimal point, then `zeros` zero characters, then the first `m` digits of D. Otherwise nothing more is written (just `0`).

The function does not write a sign and does not use `specs_.sign`, `percent` or `locale`. It must work with any output iterator as described in the context (including one that discards the characters and only counts them), and must return the iterator advanced by exactly the number of characters written.

## 3. Input specification

State as described in the context: `n >= 1`, digits are ASCII `'0'..'9'`; `exp_` roughly in `[-350, 310]` (the printed exponent magnitude stays below 10000); `precision` may be negative (none) or non-negative up to a few dozen; `format` is `general`, `exp` or `fixed`.

## 4. Output specification

Returns the output iterator after the last character written. Characters appear exactly as described in section 2.

## 5. Edge cases and constraints (examples, `point` = `.`)

Each row: digits D, `exp_`, then `specs_` (precision, trailing_zeros, format as seen by `prettify`; the constructor may already have switched `general` to `exp`, e.g. for very small numbers).

| D, exp_ | precision, trailing_zeros, format | output |
|---|---|---|
| `12345`, -3 | -1, false, general | `12.345` |
| `1234`, 3 | -1, false, general | `1234000` |
| `1234`, 3 | 8, true, fixed | `1234000.0` |
| `1234`, 3 | 10, true, general | `1234000.000` |
| `1234`, 3 | 7, true, general | `1234000.0` (nothing to pad: one `0` after the point) |
| `1234`, 3 | 7, true, fixed | `1234000.` (fixed: no zero after the point) |
| `1230`, -2 | -1, false, general | `12.3` |
| `1200`, -2 | -1, false, general | `12` |
| `1200`, -2 | 6, true, general | `12.0000` |
| `1200`, -2 | 3, true, general | `12.00` |
| `12345`, -6 | -1, false, general | `0.012345` |
| `12345`, -9 | -1, false, fixed | `0.000012345` |
| `1000`, -9 | -1, false, fixed | `0.000001` |
| `1`, -7 | 3, false, fixed | `0.0001` (zeros after the point limited to the precision) |
| `12300`, -7 | 6, true, fixed | `0.0012300` |
| `0`, 0 | 6, true, fixed | `0.00000` |
| `0`, 0 | -1, false, general | `0` |
| `12345`, 2 | -1, false, exp | `1.2345e+06` |
| `1234`, 0 | 2, true, exp | `1.234e+03` |
| `1`, 0 | 5, true, exp | `10000e+00` (no point when n == 1) |
| `12`, -20 | 3, true, exp | `1.20e-19` |

=== CONTEXT ===
# Context for the function to implement

- **Language:** C++11 (GCC 9)
- **File:** `include/fmt/format.h` (fmt 6.1.0), inside `namespace fmt { inline namespace v6 { namespace internal { ... } } }`
- **Enclosing scope:** the stub is the private member function template `prettify` of the class template `float_writer<Char>` shown below (the class and its other members are not part of your answer). Keep the stub's signature exactly; `It` is an output iterator, see below.

## Instance state (class `float_writer<Char>`)

```
template <typename Char> class float_writer {
 private:
  // The number is given as v = digits_ * pow(10, exp_).
  const char* digits_;    // the decimal digits, ASCII '0'..'9' (not NUL terminated); digits_[0] is the most significant digit
  int num_digits_;        // how many digits there are (>= 1)
  int exp_;               // decimal exponent of the last digit
  size_t size_;           // total output size (computed in the constructor by calling prettify with a counting iterator)
  float_specs specs_;     // formatting options, see below
  Char decimal_point_;    // the character to print as decimal point

  template <typename It> It prettify(It it) const;     // <-- the stub

 public:
  float_writer(const char* digits, int num_digits, int exp, float_specs specs, Char decimal_point);
  // the constructor: if specs.format == float_format::general and the number does not fit positional notation
  // (full_exp-1 < -4 or >= precision, where precision is 16 when specs.precision <= 0) it switches specs_.format to
  // float_format::exp, then calls prettify(counting_iterator()) to compute size_.
  size_t size() const;
  template <typename It> void operator()(It&& it) { if (specs_.sign) *it++ = sign char; it = prettify(it); }
};

enum class float_format : unsigned char { general, exp, fixed, hex };

struct float_specs {
  int precision;            // requested precision, negative when none
  float_format format : 8;  // see above (prettify treats general and fixed alike; hex is never passed to it)
  sign_t sign : 8;          // not used by prettify
  bool upper : 1;           // use 'E' instead of 'e' in the exponent notation
  bool locale : 1, percent : 1, binary32 : 1, use_grisu : 1;   // not used by prettify
  bool trailing_zeros : 1;  // pad with zeros up to the requested precision
};
```

## Helpers available (same namespace)

```
// Writes the exponent as a sign ('+' or '-', always present) and at least two digits; three or four digits when |exp| >= 100 / 1000:
template <typename Char, typename It> It write_exponent(int exp, It it);       // use as write_exponent<Char>(exp, it)

// Copies [first, last) converting each character to Char and returns the advanced output iterator:
template <typename Char, typename InputIt, typename OutputIt> OutputIt copy_str(InputIt first, InputIt last, OutputIt it);
```

`It` is any output iterator: a plain `Char*`, a `std::back_insert_iterator`, or `counting_iterator`, an iterator that only counts the elements written (`*it++ = x` is allowed; no other operation is). So write characters only with `*it++ = static_cast<Char>(c)`, with `copy_str<Char>(...)` and with `std::fill_n(it, count, static_cast<Char>(c))` (`<algorithm>` is available), and always continue with the iterator returned by these helpers.

## Caller (for orientation only)

```
// float_writer::operator()(It&& it):   it = prettify(it);
// float_writer constructor:            size_ = prettify(counting_iterator()).count();
```

=== STUB ===
```cpp
template <typename It> It prettify(It it) const {
    // TODO: implement according to the specification
}
```
