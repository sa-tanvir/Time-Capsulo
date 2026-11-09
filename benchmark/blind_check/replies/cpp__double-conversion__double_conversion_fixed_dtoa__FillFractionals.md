```cpp
static void FillFractionals(uint64_t fractionals, int exponent,
                            int fractional_count, Vector<char> buffer,
                            int* length, int* decimal_point) {
  if (-exponent <= 64) {
    int point = -exponent;
    for (int i = 0; i < fractional_count; ++i) {
      if (fractionals == 0) break;
      fractionals *= 5;
      point--;
      int digit = static_cast<int>(fractionals >> point);
      buffer[*length] = static_cast<char>('0' + digit);
      (*length)++;
      fractionals -= static_cast<uint64_t>(digit) << point;
    }
    if (point > 0 && ((fractionals >> (point - 1)) & 1) == 1) {
      RoundUp(buffer, length, decimal_point);
    }
  } else {
    UInt128 fractionals128 = UInt128(fractionals, 0);
    fractionals128.Shift(-exponent - 64);
    int point = 128;
    for (int i = 0; i < fractional_count; ++i) {
      if (fractionals128.IsZero()) break;
      fractionals128.Multiply(5);
      point--;
      int digit = fractionals128.DivModPowerOf2(point);
      buffer[*length] = static_cast<char>('0' + digit);
      (*length)++;
    }
    if (point > 0 && fractionals128.BitAt(point - 1) == 1) {
      RoundUp(buffer, length, decimal_point);
    }
  }
}
```
