```cpp
void Bignum::AssignPowerUInt16(uint16_t base, int power_exponent) {
  if (power_exponent == 0) {
    AssignUInt16(1);
    return;
  }
  if (base == 0) {
    Zero();
    return;
  }
  if (base == 1) {
    AssignUInt16(1);
    return;
  }
  int shifts = 0;
  uint32_t odd = base;
  while ((odd & 1) == 0) {
    odd >>= 1;
    shifts++;
  }
  if (odd == 1) {
    AssignUInt16(1);
    ShiftLeft(shifts * power_exponent);
    return;
  }
  int top = 31;
  while (((static_cast<uint32_t>(power_exponent) >> top) & 1) == 0) top--;
  AssignUInt64(odd);
  for (int bit = top - 1; bit >= 0; bit--) {
    Square();
    if ((static_cast<uint32_t>(power_exponent) >> bit) & 1) {
      MultiplyByUInt32(odd);
    }
  }
  ShiftLeft(shifts * power_exponent);
}
```
