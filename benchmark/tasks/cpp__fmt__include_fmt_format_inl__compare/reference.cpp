friend int compare(const bigint& lhs, const bigint& rhs) {
  int num_lhs_bigits = lhs.num_bigits(), num_rhs_bigits = rhs.num_bigits();
  if (num_lhs_bigits != num_rhs_bigits)
    return num_lhs_bigits > num_rhs_bigits ? 1 : -1;
  int i = static_cast<int>(lhs.bigits_.size()) - 1;
  int j = static_cast<int>(rhs.bigits_.size()) - 1;
  int end = i - j;
  if (end < 0) end = 0;
  for (; i >= end; --i, --j) {
    bigit lhs_bigit = lhs.bigits_[i], rhs_bigit = rhs.bigits_[j];
    if (lhs_bigit != rhs_bigit) return lhs_bigit > rhs_bigit ? 1 : -1;
  }
  if (i != j) return i > j ? 1 : -1;
  return 0;
}
