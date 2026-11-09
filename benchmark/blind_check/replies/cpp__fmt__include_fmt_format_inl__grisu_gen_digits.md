```cpp
FMT_ALWAYS_INLINE digits::result grisu_gen_digits(fp value, uint64_t error,
                                                  int& exp, Handler& handler) {
  const int shift = -value.e;
  const uint64_t one = 1ULL << shift;
  uint32_t integral = static_cast<uint32_t>(value.f >> shift);
  FMT_ASSERT(integral != 0, "");
  FMT_ASSERT(integral == value.f >> shift, "");
  uint64_t fractional = value.f & (one - 1);
  exp = count_digits(integral);
  digits::result result = handler.on_start(
      data::powers_of_10_64[exp - 1] << shift, value.f / 10, error * 10, exp);
  if (result != digits::more) return result;
  // Generate digits for the integral part.
  while (exp > 0) {
    uint32_t divisor = static_cast<uint32_t>(data::powers_of_10_64[exp - 1]);
    uint32_t digit = integral / divisor;
    integral %= divisor;
    --exp;
    uint64_t remainder = (static_cast<uint64_t>(integral) << shift) + fractional;
    result = handler.on_digit(static_cast<char>('0' + digit),
                              data::powers_of_10_64[exp] << shift, remainder,
                              error, exp, true);
    if (result != digits::more) return result;
  }
  // Generate digits for the fractional part.
  for (;;) {
    fractional *= 10;
    error *= 10;
    char digit = static_cast<char>('0' + (fractional >> shift));
    fractional &= one - 1;
    --exp;
    result = handler.on_digit(digit, one, fractional, error, exp, false);
    if (result != digits::more) return result;
  }
}
```
