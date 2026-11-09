```cpp
static double RadixStringToIeee(Iterator* current,
                                Iterator end,
                                bool sign,
                                uc16 separator,
                                bool parse_as_hex_float,
                                bool allow_trailing_junk,
                                double junk_string_value,
                                bool read_as_double,
                                bool* result_is_junk) {
  const int kSignificandSize = read_as_double ? Double::kSignificandSize
                                              : Single::kSignificandSize;
  const int radix = 1 << radix_log_2;

  *result_is_junk = true;

  // Skip leading zeros.
  while (**current == '0') {
    if (Advance(current, separator, radix, end)) {
      *result_is_junk = false;
      return SignedZero(sign);
    }
  }

  uint64_t number = 0;
  int exponent = 0;
  bool seen_point = false;

  while (true) {
    int c = static_cast<int>(**current);
    int digit;
    if (IsDecimalDigitForRadix(c, radix)) {
      digit = c - '0';
    } else if (IsCharacterDigitForRadix(c, radix, 'a')) {
      digit = c - 'a' + 10;
    } else if (IsCharacterDigitForRadix(c, radix, 'A')) {
      digit = c - 'A' + 10;
    } else if (parse_as_hex_float && c == '.' && !seen_point) {
      seen_point = true;
      if (Advance(current, separator, radix, end)) break;
      continue;
    } else {
      break;
    }

    number = number * radix + digit;
    if (seen_point) exponent -= radix_log_2;
    uint64_t overflow = number >> kSignificandSize;
    if (overflow != 0) {
      int overflow_bits_count = 1;
      while (overflow > 1) {
        overflow_bits_count++;
        overflow >>= 1;
      }
      uint64_t dropped_bits_mask = (static_cast<uint64_t>(1) << overflow_bits_count) - 1;
      uint64_t dropped_bits = number & dropped_bits_mask;
      number >>= overflow_bits_count;
      exponent += overflow_bits_count;

      bool zero_tail = true;
      for (;;) {
        if (Advance(current, separator, radix, end)) break;
        int d = static_cast<int>(**current);
        if (parse_as_hex_float && d == '.' && !seen_point) {
          seen_point = true;
          continue;
        }
        if (!isDigit(d, radix)) break;
        zero_tail = zero_tail && d == '0';
        if (!seen_point) exponent += radix_log_2;
      }

      uint64_t middle_value = static_cast<uint64_t>(1) << (overflow_bits_count - 1);
      if (dropped_bits > middle_value) {
        number++;
      } else if (dropped_bits == middle_value) {
        if ((number & 1) != 0 || !zero_tail) number++;
      }
      if ((number & (static_cast<uint64_t>(1) << kSignificandSize)) != 0) {
        exponent++;
        number >>= 1;
      }
      break;
    }
    if (Advance(current, separator, radix, end)) break;
  }

  if (parse_as_hex_float) {
    if (*current != end && (**current == 'p' || **current == 'P')) {
      bool exp_negative = false;
      bool ok = !Advance(current, separator, radix, end);
      if (ok && (**current == '+' || **current == '-')) {
        exp_negative = (**current == '-');
        ok = !Advance(current, separator, radix, end);
      }
      int64_t e = 0;
      while (ok && isDigit(static_cast<int>(**current), 10)) {
        if (e < 100000000) e = e * 10 + (static_cast<int>(**current) - '0');
        ok = !Advance(current, separator, radix, end);
      }
      int64_t total = static_cast<int64_t>(exponent) + (exp_negative ? -e : e);
      if (total > 5000) total = 5000;
      if (total < -5000) total = -5000;
      exponent = static_cast<int>(total);
    }
    *result_is_junk = false;
    if (number == 0) return SignedZero(sign);
    double value = Double(DiyFp(number, exponent)).value();
    return sign ? -value : value;
  }

  if (!allow_trailing_junk && AdvanceToNonspace(current, end)) {
    *result_is_junk = true;
    return junk_string_value;
  }

  *result_is_junk = false;
  if (number == 0) return SignedZero(sign);
  double value;
  if (exponent == 0) {
    value = static_cast<double>(number);
  } else {
    value = Double(DiyFp(number, exponent)).value();
  }
  return sign ? -value : value;
}
```
