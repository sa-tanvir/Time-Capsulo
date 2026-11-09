bool DoubleToStringConverter::ToExponential(
    double value,
    int requested_digits,
    StringBuilder* result_builder) const {
  if (Double(value).IsSpecial()) {
    return HandleSpecialValues(value, result_builder);
  }

  if (requested_digits < -1) return false;
  if (requested_digits > kMaxExponentialDigits) return false;

  int decimal_point;
  bool sign;
  // Add space for digit before the decimal point and the '\0' character.
  const int kDecimalRepCapacity = kMaxExponentialDigits + 2;
  ASSERT(kDecimalRepCapacity > kBase10MaximalLength);
  char decimal_rep[kDecimalRepCapacity];
#ifndef NDEBUG
  // Problem: there is an assert in StringBuilder::AddSubstring() that
  // will pass this buffer to strlen(), and this buffer is not generally
  // null-terminated.
  memset(decimal_rep, 0, sizeof(decimal_rep));
#endif
  int decimal_rep_length;

  if (requested_digits == -1) {
    DoubleToAscii(value, SHORTEST, 0,
                  decimal_rep, kDecimalRepCapacity,
                  &sign, &decimal_rep_length, &decimal_point);
  } else {
    DoubleToAscii(value, PRECISION, requested_digits + 1,
                  decimal_rep, kDecimalRepCapacity,
                  &sign, &decimal_rep_length, &decimal_point);
    ASSERT(decimal_rep_length <= requested_digits + 1);

    for (int i = decimal_rep_length; i < requested_digits + 1; ++i) {
      decimal_rep[i] = '0';
    }
    decimal_rep_length = requested_digits + 1;
  }

  bool unique_zero = ((flags_ & UNIQUE_ZERO) != 0);
  if (sign && (value != 0.0 || !unique_zero)) {
    result_builder->AddCharacter('-');
  }

  int exponent = decimal_point - 1;
  CreateExponentialRepresentation(decimal_rep,
                                  decimal_rep_length,
                                  exponent,
                                  result_builder);
  return true;
}
