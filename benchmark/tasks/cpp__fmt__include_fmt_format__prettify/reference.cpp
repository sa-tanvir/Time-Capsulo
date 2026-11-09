  template <typename It> It prettify(It it) const {
    // pow(10, full_exp - 1) <= v <= pow(10, full_exp).
    int full_exp = num_digits_ + exp_;
    if (specs_.format == float_format::exp) {
      // Insert a decimal point after the first digit and add an exponent.
      *it++ = static_cast<Char>(*digits_);
      if (num_digits_ > 1) *it++ = decimal_point_;
      it = copy_str<Char>(digits_ + 1, digits_ + num_digits_, it);
      int num_zeros = specs_.precision - num_digits_;
      if (num_zeros > 0 && specs_.trailing_zeros)
        it = std::fill_n(it, num_zeros, static_cast<Char>('0'));
      *it++ = static_cast<Char>(specs_.upper ? 'E' : 'e');
      return write_exponent<Char>(full_exp - 1, it);
    }
    if (num_digits_ <= full_exp) {
      // 1234e7 -> 12340000000[.0+]
      it = copy_str<Char>(digits_, digits_ + num_digits_, it);
      it = std::fill_n(it, full_exp - num_digits_, static_cast<Char>('0'));
      if (specs_.trailing_zeros) {
        *it++ = decimal_point_;
        int num_zeros = specs_.precision - full_exp;
        if (num_zeros <= 0) {
          if (specs_.format != float_format::fixed)
            *it++ = static_cast<Char>('0');
          return it;
        }
#ifdef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
        if (num_zeros > 1000)
          throw std::runtime_error("fuzz mode - avoiding excessive cpu use");
#endif
        it = std::fill_n(it, num_zeros, static_cast<Char>('0'));
      }
    } else if (full_exp > 0) {
      // 1234e-2 -> 12.34[0+]
      it = copy_str<Char>(digits_, digits_ + full_exp, it);
      if (!specs_.trailing_zeros) {
        // Remove trailing zeros.
        int num_digits = num_digits_;
        while (num_digits > full_exp && digits_[num_digits - 1] == '0')
          --num_digits;
        if (num_digits != full_exp) *it++ = decimal_point_;
        return copy_str<Char>(digits_ + full_exp, digits_ + num_digits, it);
      }
      *it++ = decimal_point_;
      it = copy_str<Char>(digits_ + full_exp, digits_ + num_digits_, it);
      if (specs_.precision > num_digits_) {
        // Add trailing zeros.
        int num_zeros = specs_.precision - num_digits_;
        it = std::fill_n(it, num_zeros, static_cast<Char>('0'));
      }
    } else {
      // 1234e-6 -> 0.001234
      *it++ = static_cast<Char>('0');
      int num_zeros = -full_exp;
      if (specs_.precision >= 0 && specs_.precision < num_zeros)
        num_zeros = specs_.precision;
      int num_digits = num_digits_;
      if (!specs_.trailing_zeros)
        while (num_digits > 0 && digits_[num_digits - 1] == '0') --num_digits;
      if (num_zeros != 0 || num_digits != 0) {
        *it++ = decimal_point_;
        it = std::fill_n(it, num_zeros, static_cast<Char>('0'));
        it = copy_str<Char>(digits_, digits_ + num_digits, it);
      }
    }
    return it;
  }
