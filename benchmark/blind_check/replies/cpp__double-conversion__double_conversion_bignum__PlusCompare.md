```cpp
int Bignum::PlusCompare(const Bignum& a, const Bignum& b, const Bignum& c) {
  // Make a the one with the larger BigitLength (or equal).
  const Bignum* pa = &a;
  const Bignum* pb = &b;
  if (pa->BigitLength() < pb->BigitLength()) {
    const Bignum* t = pa; pa = pb; pb = t;
  }
  const int a_len = pa->BigitLength();
  const int b_len = pb->BigitLength();
  const int c_len = c.BigitLength();
  // a + b < 2 * 2^(28*a_len) and a + b >= 2^(28*(a_len-1)) if a nonzero.
  if (a_len + 1 < c_len) return -1;
  if (a_len > c_len) {
    // a >= 2^(28*(a_len-1)) >= 2^(28*c_len) > c.
    return 1;
  }
  if (a_len == 0) {
    // all of a, b are zero
    return (c_len == 0) ? 0 : -1;
  }
  // Now c_len is in {a_len, a_len + 1}. Process from the most significant
  // bigit down, tracking the difference "c - (a+b)" truncated to prefix.
  int lowest = pa->exponent_;
  if (pb->exponent_ < lowest && b_len > 0) lowest = pb->exponent_;
  if (c.exponent_ < lowest) lowest = c.exponent_;
  if (b_len == 0) lowest = Min(pa->exponent_, c.exponent_);
  // Compute sum bigits from the low end to know the carries, but we need
  // a top-down comparison; do a bottom-up pass computing sign instead.
  // borrow-style: compute c - (a + b) from the low end, tracking whether
  // the result so far (on the processed low digits) is <0, 0, >0.
  // Use carry on the sum side and process digit-by-digit.
  int top = Max(a_len + 1, c_len);
  int cmp = 0;  // comparison of low part of (a+b) vs low part of c
  Chunk carry = 0;
  for (int i = lowest; i < top; i++) {
    Chunk sum = pa->BigitAt(i) + pb->BigitAt(i) + carry;
    carry = sum >> kBigitSize;
    sum &= kBigitMask;
    Chunk cv = c.BigitAt(i);
    if (sum < cv) cmp = -1;
    else if (sum > cv) cmp = 1;
  }
  if (carry != 0) return 1;
  return cmp;
}
```
