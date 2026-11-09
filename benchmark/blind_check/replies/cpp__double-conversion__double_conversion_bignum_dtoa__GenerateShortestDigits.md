```cpp
static void GenerateShortestDigits(Bignum* numerator, Bignum* denominator,
                                   Bignum* delta_minus, Bignum* delta_plus,
                                   bool is_even,
                                   Vector<char> buffer, int* length) {
  *length = 0;
  for (;;) {
    uint16_t digit = numerator->DivideModuloIntBignum(*denominator);
    buffer[(*length)++] = static_cast<char>(digit + '0');
    bool in_delta_room_minus;
    bool in_delta_room_plus;
    if (is_even) {
      in_delta_room_minus = Bignum::LessEqual(*numerator, *delta_minus);
    } else {
      in_delta_room_minus = Bignum::Less(*numerator, *delta_minus);
    }
    if (is_even) {
      in_delta_room_plus =
          Bignum::PlusCompare(*numerator, *delta_plus, *denominator) >= 0;
    } else {
      in_delta_room_plus =
          Bignum::PlusCompare(*numerator, *delta_plus, *denominator) > 0;
    }
    if (!in_delta_room_minus && !in_delta_room_plus) {
      numerator->Times10();
      delta_minus->Times10();
      delta_plus->Times10();
    } else if (in_delta_room_minus && in_delta_room_plus) {
      int compare = Bignum::PlusCompare(*numerator, *numerator, *denominator);
      if (compare < 0) {
        // keep digits
      } else if (compare > 0) {
        buffer[(*length) - 1]++;
      } else {
        if (((buffer[(*length) - 1] - '0') & 1) != 0) {
          buffer[(*length) - 1]++;
        }
      }
      return;
    } else if (in_delta_room_minus) {
      return;
    } else {
      buffer[(*length) - 1]++;
      return;
    }
  }
}
```
