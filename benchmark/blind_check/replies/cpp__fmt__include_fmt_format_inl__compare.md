```cpp
friend int compare(const bigint& lhs, const bigint& rhs) {
  int num_lhs_bigits = lhs.num_bigits(), num_rhs_bigits = rhs.num_bigits();
  if (num_lhs_bigits != num_rhs_bigits)
    return num_lhs_bigits > num_rhs_bigits ? 1 : -1;
  int lhs_exp = lhs.exp_, rhs_exp = rhs.exp_;
  int end = lhs_exp < rhs_exp ? lhs_exp : rhs_exp;
  for (int k = num_lhs_bigits - 1; k >= end; --k) {
    bigit a = k >= lhs_exp ? lhs.bigits_[k - lhs_exp] : 0;
    bigit b = k >= rhs_exp ? rhs.bigits_[k - rhs_exp] : 0;
    if (a != b) return a > b ? 1 : -1;
  }
  return 0;
}
```
