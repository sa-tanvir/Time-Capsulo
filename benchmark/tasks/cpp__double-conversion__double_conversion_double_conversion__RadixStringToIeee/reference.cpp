static double RadixStringToIeee(Iterator* current,
                                Iterator end,
                                bool sign,
                                uc16 separator,
                                bool parse_as_hex_float,
                                bool allow_trailing_junk,
                                double junk_string_value,
                                bool read_as_double,
                                bool* result_is_junk) {
  ASSERT(*current != end);
  ASSERT(!parse_as_hex_float ||
      IsHexFloatString(*current, end, separator, allow_trailing_junk));

  const int kDoubleSize = Double::kSignificandSize;
  const int kSingleSize = Single::kSignificandSize;
  const int kSignificandSize = read_as_double? kDoubleSize: kSingleSize;

  *result_is_junk = true;

  int64_t number = 0;
  int exponent = 0;
  const int radix = (1 << radix_log_2);
  // Whether we have encountered a '.' and are parsing the decimal digits.
  // Only relevant if parse_as_hex_float is true.
  bool post_decimal = false;

  // Skip leading 0s.
  while (**current == '0') {
    if (Advance(current, separator, radix, end)) {
      *result_is_junk = false;
      return SignedZero(sign);
    }
  }

  while (true) {
    int digit;
    if (IsDecimalDigitForRadix(**current, radix)) {
      digit = static_cast<char>(**current) - '0';
      if (post_decimal) exponent -= radix_log_2;
    } else if (IsCharacterDigitForRadix(**current, radix, 'a')) {
      digit = static_cast<char>(**current) - 'a' + 10;
      if (post_decimal) exponent -= radix_log_2;
    } else if (IsCharacterDigitForRadix(**current, radix, 'A')) {
      digit = static_cast<char>(**current) - 'A' + 10;
      if (post_decimal) exponent -= radix_log_2;
    } else if (parse_as_hex_float && **current == '.') {
      post_decimal = true;
      Advance(current, separator, radix, end);
      ASSERT(*current != end);
      continue;
    } else if (parse_as_hex_float && (**current == 'p' || **current == 'P')) {
      break;
    } else {
      if (allow_trailing_junk || !AdvanceToNonspace(current, end)) {
        break;
      } else {
        return junk_string_value;
      }
    }

    number = number * radix + digit;
    int overflow = static_cast<int>(number >> kSignificandSize);
    if (overflow != 0) {
      // Overflow occurred. Need to determine which direction to round the
      // result.
      int overflow_bits_count = 1;
      while (overflow > 1) {
        overflow_bits_count++;
        overflow >>= 1;
      }

      int dropped_bits_mask = ((1 << overflow_bits_count) - 1);
      int dropped_bits = static_cast<int>(number) & dropped_bits_mask;
      number >>= overflow_bits_count;
      exponent += overflow_bits_count;

      bool zero_tail = true;
      for (;;) {
        if (Advance(current, separator, radix, end)) break;
        if (parse_as_hex_float && **current == '.') {
          // Just run over the '.'. We are just trying to see whether there is
          // a non-zero digit somewhere.
          Advance(current, separator, radix, end);
          ASSERT(*current != end);
          post_decimal = true;
        }
        if (!isDigit(**current, radix)) break;
        zero_tail = zero_tail && **current == '0';
        if (!post_decimal) exponent += radix_log_2;
      }

      if (!parse_as_hex_float &&
          !allow_trailing_junk &&
          AdvanceToNonspace(current, end)) {
        return junk_string_value;
      }

      int middle_value = (1 << (overflow_bits_count - 1));
      if (dropped_bits > middle_value) {
        number++;  // Rounding up.
      } else if (dropped_bits == middle_value) {
        // Rounding to even to consistency with decimals: half-way case rounds
        // up if significant part is odd and down otherwise.
        if ((number & 1) != 0 || !zero_tail) {
          number++;  // Rounding up.
        }
      }

      // Rounding up may cause overflow.
      if ((number & ((int64_t)1 << kSignificandSize)) != 0) {
        exponent++;
        number >>= 1;
      }
      break;
    }
    if (Advance(current, separator, radix, end)) break;
  }

  ASSERT(number < ((int64_t)1 << kSignificandSize));
  ASSERT(static_cast<int64_t>(static_cast<double>(number)) == number);

  *result_is_junk = false;

  if (parse_as_hex_float) {
    ASSERT(**current == 'p' || **current == 'P');
    Advance(current, separator, radix, end);
    ASSERT(*current != end);
    bool is_negative = false;
    if (**current == '+') {
      Advance(current, separator, radix, end);
      ASSERT(*current != end);
    } else if (**current == '-') {
      is_negative = true;
      Advance(current, separator, radix, end);
      ASSERT(*current != end);
    }
    int written_exponent = 0;
    while (IsDecimalDigitForRadix(**current, 10)) {
      // No need to read exponents if they are too big. That could potentially overflow
      // the `written_exponent` variable.
      if (abs(written_exponent) <= 100 * Double::kMaxExponent) {
        written_exponent = 10 * written_exponent + **current - '0';
      }
      if (Advance(current, separator, radix, end)) break;
    }
    if (is_negative) written_exponent = -written_exponent;
    exponent += written_exponent;
  }

  if (exponent == 0 || number == 0) {
    if (sign) {
      if (number == 0) return -0.0;
      number = -number;
    }
    return static_cast<double>(number);
  }

  ASSERT(number != 0);
  double result = Double(DiyFp(number, exponent)).value();
  return sign ? -result : result;
}
