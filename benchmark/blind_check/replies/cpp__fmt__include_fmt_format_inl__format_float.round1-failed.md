```cpp
int format_float(T value, int precision, float_specs specs, buffer<char>& buf) {
  FMT_ASSERT(value >= 0, "value is negative");
  if (value == 0) {
    if (precision <= 0 || specs.format != float_format::fixed) {
      buf.resize(1);
      buf[0] = '0';
      return 0;
    }
    buf.resize(to_unsigned(precision));
    for (int i = 0; i < precision; ++i) buf[to_unsigned(i)] = '0';
    return -precision;
  }
  if (!specs.use_grisu) return snprintf_float(value, precision, specs, buf);
  int exp = 0;
  if (precision != -1) {
    if (precision > 17) return snprintf_float(value, precision, specs, buf);
    const int min_exp = -60;
    int cached_exp10 = 0;
    fp normalized = normalize(fp(value));
    const fp cached_pow = get_cached_power(
        min_exp - (normalized.e + fp::significand_size), cached_exp10);
    normalized = normalized * cached_pow;
    bool fixed = specs.format == float_format::fixed;
    buf.resize(buf.capacity() < 40 ? 0 : 0);
    buf.reserve(64);
    fixed_handler handler{buf.data(), 0, precision, -cached_exp10, fixed};
    if (grisu_gen_digits(normalized, 1, exp, handler) == digits::error)
      return snprintf_float(value, precision, specs, buf);
    int num_digits = handler.size;
    if (fixed) {
      buf.resize(to_unsigned(num_digits));
      return -precision;
    }
    exp += handler.exp10;
    // Remove trailing zeros.
    while (num_digits > 1 && buf[to_unsigned(num_digits - 1)] == '0') {
      --num_digits;
      ++exp;
    }
    buf.resize(to_unsigned(num_digits));
    return exp;
  }
  // Shortest representation.
  if (specs.binary32)
    fallback_format(static_cast<float>(value), buf, exp);
  else
    fallback_format(value, buf, exp);
  return exp;
}
```
