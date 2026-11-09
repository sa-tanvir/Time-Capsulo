```cpp
static bool RoundWeedCounted(Vector<char> buffer,
                             int length,
                             uint64_t rest,
                             uint64_t ten_kappa,
                             uint64_t unit,
                             int* kappa) {
  if (unit >= ten_kappa) return false;
  if (ten_kappa - unit <= unit) return false;
  if ((ten_kappa - rest > rest) && (ten_kappa - 2 * rest >= 2 * unit)) {
    return true;
  }
  if ((rest > unit) && (ten_kappa - (rest - unit) <= (rest - unit))) {
    buffer[length - 1]++;
    for (int i = length - 1; i > 0; --i) {
      if (buffer[i] != '0' + 10) break;
      buffer[i] = '0';
      buffer[i - 1]++;
    }
    if (buffer[0] == '0' + 10) {
      buffer[0] = '1';
      (*kappa) += 1;
    }
    return true;
  }
  return false;
}
```
