static void FillFractionals(uint64_t fractionals, int exponent,
                            int fractional_count, Vector<char> buffer,
                            int* length, int* decimal_point) {
  ASSERT(-128 <= exponent && exponent <= 0);
  // 'fractionals' is a fixed-point number, with binary point at bit
  // (-exponent). Inside the function the non-converted remainder of fractionals
  // is a fixed-point number, with binary point at bit 'point'.
  if (-exponent <= 64) {
    // One 64 bit number is sufficient.
    ASSERT(fractionals >> 56 == 0);
    int point = -exponent;
    for (int i = 0; i < fractional_count; ++i) {
      if (fractionals == 0) break;
      // Instead of multiplying by 10 we multiply by 5 and adjust the point
      // location. This way the fractionals variable will not overflow.
      // Invariant at the beginning of the loop: fractionals < 2^point.
      // Initially we have: point <= 64 and fractionals < 2^56
      // After each iteration the point is decremented by one.
      // Note that 5^3 = 125 < 128 = 2^7.
      // Therefore three iterations of this loop will not overflow fractionals
      // (even without the subtraction at the end of the loop body). At this
      // time point will satisfy point <= 61 and therefore fractionals < 2^point
      // and any further multiplication of fractionals by 5 will not overflow.
      fractionals *= 5;
      point--;
      int digit = static_cast<int>(fractionals >> point);
      ASSERT(digit <= 9);
      buffer[*length] = static_cast<char>('0' + digit);
      (*length)++;
      fractionals -= static_cast<uint64_t>(digit) << point;
    }
    // If the first bit after the point is set we have to round up.
    ASSERT(fractionals == 0 || point - 1 >= 0);
    if ((fractionals != 0) && ((fractionals >> (point - 1)) & 1) == 1) {
      RoundUp(buffer, length, decimal_point);
    }
  } else {  // We need 128 bits.
    ASSERT(64 < -exponent && -exponent <= 128);
    UInt128 fractionals128 = UInt128(fractionals, 0);
    fractionals128.Shift(-exponent - 64);
    int point = 128;
    for (int i = 0; i < fractional_count; ++i) {
      if (fractionals128.IsZero()) break;
      // As before: instead of multiplying by 10 we multiply by 5 and adjust the
      // point location.
      // This multiplication will not overflow for the same reasons as before.
      fractionals128.Multiply(5);
      point--;
      int digit = fractionals128.DivModPowerOf2(point);
      ASSERT(digit <= 9);
      buffer[*length] = static_cast<char>('0' + digit);
      (*length)++;
    }
    if (fractionals128.BitAt(point - 1) == 1) {
      RoundUp(buffer, length, decimal_point);
    }
  }
}
