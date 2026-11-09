```cpp
digits::result on_digit(char digit, uint64_t divisor, uint64_t remainder,
                        uint64_t error, int, bool integral) {
  FMT_ASSERT(remainder < divisor, "");
  buf[size++] = digit;
  if (size < precision) return digits::more;
  if (!integral) {
    // Check if error * 2 < divisor with overflow prevention.
    if (error >= divisor || error >= divisor - error) return digits::error;
  } else {
    FMT_ASSERT(error == 1 && divisor > 2, "");
  }
  auto dir = get_round_direction(divisor, remainder, error);
  if (dir != up) return dir == down ? digits::done : digits::error;
  ++buf[size - 1];
  for (int i = size - 1; i > 0 && buf[i] > '9'; --i) {
    buf[i] = '0';
    ++buf[i - 1];
  }
  if (buf[0] > '9') {
    buf[0] = '1';
    buf[size++] = '0';
  }
  return digits::done;
}
```
