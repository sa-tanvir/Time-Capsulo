```cpp
bool DoubleToStringConverter::ToPrecision(double value,
                                          int precision,
                                          StringBuilder* result_builder) const {
  if (Double(value).IsSpecial()) {
    return HandleSpecialValues(value, result_builder);
  }
  if (precision < kMinPrecisionDigits || precision > kMaxPrecisionDigits) {
    return false;
  }

  bool sign;
  int decimal_point;
  int decimal_rep_length;
  const int kDecimalRepCapacity = kMaxPrecisionDigits + 1;
  char decimal_rep[kDecimalRepCapacity];
  DoubleToAscii(value, PRECISION, precision,
                decimal_rep, kDecimalRepCapacity,
                &sign, &decimal_rep_length, &decimal_point);

  bool unique_zero = ((flags_ & UNIQUE_ZERO) != 0);
  if (sign && (value != 0.0 || !unique_zero)) {
    result_builder->AddCharacter('-');
  }

  int exponent = decimal_point - 1;
  int extra_zero = ((flags_ & EMIT_TRAILING_ZERO_AFTER_POINT) != 0) ? 1 : 0;
  if ((-decimal_point + 1 > max_leading_padding_zeroes_in_precision_mode_) ||
      (decimal_point - precision + extra_zero >
       max_trailing_padding_zeroes_in_precision_mode_)) {
    for (int i = decimal_rep_length; i < precision; ++i) {
      decimal_rep[i] = '0';
    }
    CreateExponentialRepresentation(decimal_rep, precision, exponent,
                                    result_builder);
  } else {
    CreateDecimalRepresentation(decimal_rep, decimal_rep_length, decimal_point,
                                Max(0, precision - decimal_point),
                                result_builder);
  }
  return true;
}
```
