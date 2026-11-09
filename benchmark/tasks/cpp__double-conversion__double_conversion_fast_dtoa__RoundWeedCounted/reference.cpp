static bool RoundWeedCounted(Vector<char> buffer,
                             int length,
                             uint64_t rest,
                             uint64_t ten_kappa,
                             uint64_t unit,
                             int* kappa) {
  ASSERT(rest < ten_kappa);
  // The following tests are done in a specific order to avoid overflows. They
  // will work correctly with any uint64 values of rest < ten_kappa and unit.
  //
  // If the unit is too big, then we don't know which way to round. For example
  // a unit of 50 means that the real number lies within rest +/- 50. If
  // 10^kappa == 40 then there is no way to tell which way to round.
  if (unit >= ten_kappa) return false;
  // Even if unit is just half the size of 10^kappa we are already completely
  // lost. (And after the previous test we know that the expression will not
  // over/underflow.)
  if (ten_kappa - unit <= unit) return false;
  // If 2 * (rest + unit) <= 10^kappa we can safely round down.
  if ((ten_kappa - rest > rest) && (ten_kappa - 2 * rest >= 2 * unit)) {
    return true;
  }
  // If 2 * (rest - unit) >= 10^kappa, then we can safely round up.
  if ((rest > unit) && (ten_kappa - (rest - unit) <= (rest - unit))) {
    // Increment the last digit recursively until we find a non '9' digit.
    buffer[length - 1]++;
    for (int i = length - 1; i > 0; --i) {
      if (buffer[i] != '0' + 10) break;
      buffer[i] = '0';
      buffer[i - 1]++;
    }
    // If the first digit is now '0'+ 10 we had a buffer with all '9's. With the
    // exception of the first digit all digits are now '0'. Simply switch the
    // first digit to '1' and adjust the kappa. Example: "99" becomes "10" and
    // the power (the kappa) is increased.
    if (buffer[0] == '0' + 10) {
      buffer[0] = '1';
      (*kappa) += 1;
    }
    return true;
  }
  return false;
}
