int format_float(T value, int precision, float_specs specs, buffer<char>& buf) {
  static_assert(!std::is_same<T, float>(), "");
  FMT_ASSERT(value >= 0, "value is negative");

  const bool fixed = specs.format == float_format::fixed;
  if (value <= 0) {  // <= instead of == to silence a warning.
    if (precision <= 0 || !fixed) {
      buf.push_back('0');
      return 0;
    }
    buf.resize(to_unsigned(precision));
    std::uninitialized_fill_n(buf.data(), precision, '0');
    return -precision;
  }

  if (!specs.use_grisu) return snprintf_float(value, precision, specs, buf);

  int exp = 0;
  const int min_exp = -60;  // alpha in Grisu.
  int cached_exp10 = 0;     // K in Grisu.
  if (precision != -1) {
    if (precision > 17) return snprintf_float(value, precision, specs, buf);
    fp normalized = normalize(fp(value));
    const auto cached_pow = get_cached_power(
        min_exp - (normalized.e + fp::significand_size), cached_exp10);
    normalized = normalized * cached_pow;
    fixed_handler handler{buf.data(), 0, precision, -cached_exp10, fixed};
    if (grisu_gen_digits(normalized, 1, exp, handler) == digits::error)
      return snprintf_float(value, precision, specs, buf);
    int num_digits = handler.size;
    if (!fixed) {
      // Remove trailing zeros.
      while (num_digits > 0 && buf[num_digits - 1] == '0') {
        --num_digits;
        ++exp;
      }
    }
    buf.resize(to_unsigned(num_digits));
  } else {
    fp fp_value;
    auto boundaries = specs.binary32
                          ? fp_value.assign_float_with_boundaries(value)
                          : fp_value.assign_with_boundaries(value);
    fp_value = normalize(fp_value);
    // Find a cached power of 10 such that multiplying value by it will bring
    // the exponent in the range [min_exp, -32].
    const fp cached_pow = get_cached_power(
        min_exp - (fp_value.e + fp::significand_size), cached_exp10);
    // Multiply value and boundaries by the cached power of 10.
    fp_value = fp_value * cached_pow;
    boundaries.lower = multiply(boundaries.lower, cached_pow.f);
    boundaries.upper = multiply(boundaries.upper, cached_pow.f);
    assert(min_exp <= fp_value.e && fp_value.e <= -32);
    --boundaries.lower;  // \tilde{M}^- - 1 ulp -> M^-_{\downarrow}.
    ++boundaries.upper;  // \tilde{M}^+ + 1 ulp -> M^+_{\uparrow}.
    // Numbers outside of (lower, upper) definitely do not round to value.
    grisu_shortest_handler handler{buf.data(), 0,
                                   boundaries.upper - fp_value.f};
    auto result =
        grisu_gen_digits(fp(boundaries.upper, fp_value.e),
                         boundaries.upper - boundaries.lower, exp, handler);
    if (result == digits::error) {
      exp += handler.size - cached_exp10 - 1;
      fallback_format(value, buf, exp);
      return exp;
    }
    buf.resize(to_unsigned(handler.size));
  }
  return exp - cached_exp10;
}
