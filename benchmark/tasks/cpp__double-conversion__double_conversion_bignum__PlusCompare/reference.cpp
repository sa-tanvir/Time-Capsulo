int Bignum::PlusCompare(const Bignum& a, const Bignum& b, const Bignum& c) {
  ASSERT(a.IsClamped());
  ASSERT(b.IsClamped());
  ASSERT(c.IsClamped());
  if (a.BigitLength() < b.BigitLength()) {
    return PlusCompare(b, a, c);
  }
  if (a.BigitLength() + 1 < c.BigitLength()) return -1;
  if (a.BigitLength() > c.BigitLength()) return +1;
  // The exponent encodes 0-bigits. So if there are more 0-digits in 'a' than
  // 'b' has digits, then the bigit-length of 'a'+'b' must be equal to the one
  // of 'a'.
  if (a.exponent_ >= b.BigitLength() && a.BigitLength() < c.BigitLength()) {
    return -1;
  }

  Chunk borrow = 0;
  // Starting at min_exponent all digits are == 0. So no need to compare them.
  int min_exponent = Min(Min(a.exponent_, b.exponent_), c.exponent_);
  for (int i = c.BigitLength() - 1; i >= min_exponent; --i) {
    Chunk chunk_a = a.BigitAt(i);
    Chunk chunk_b = b.BigitAt(i);
    Chunk chunk_c = c.BigitAt(i);
    Chunk sum = chunk_a + chunk_b;
    if (sum > chunk_c + borrow) {
      return +1;
    } else {
      borrow = chunk_c + borrow - sum;
      if (borrow > 1) return -1;
      borrow <<= kBigitSize;
    }
  }
  if (borrow == 0) return 0;
  return -1;
}
