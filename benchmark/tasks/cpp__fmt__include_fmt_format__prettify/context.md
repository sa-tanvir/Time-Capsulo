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
