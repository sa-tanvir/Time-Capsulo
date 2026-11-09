```cpp
static bool RoundWeed(Vector<char> buffer,
                      int length,
                      uint64_t distance_too_high_w,
                      uint64_t unsafe_interval,
                      uint64_t rest,
                      uint64_t ten_kappa,
                      uint64_t unit) {
  uint64_t small_distance = distance_too_high_w - unit;
  uint64_t big_distance = distance_too_high_w + unit;
  while (rest < small_distance &&
         unsafe_interval - rest >= ten_kappa &&
         (rest + ten_kappa < small_distance ||
          small_distance - rest >= rest + ten_kappa - small_distance)) {
    buffer[length - 1]--;
    rest += ten_kappa;
  }
  if (rest < big_distance &&
      unsafe_interval - rest >= ten_kappa &&
      (rest + ten_kappa < big_distance ||
       big_distance - rest > rest + ten_kappa - big_distance)) {
    return false;
  }
  return (2 * unit <= rest) && (rest <= unsafe_interval - 4 * unit);
}
```
