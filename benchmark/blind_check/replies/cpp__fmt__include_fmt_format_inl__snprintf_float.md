```cpp
int snprintf_float(T value, int precision, float_specs specs,
                   buffer<char>& buf) {
  FMT_ASSERT(buf.capacity() > buf.size(), "empty buffer");
  static_assert(!std::is_same<T, float>::value, "");

  // Build the printf format string.
  char format[8];
  char* fp = format;
  *fp++ = '%';
  if (specs.trailing_zeros) *fp++ = '#';
  *fp++ = '.';
  *fp++ = '*';
  if (std::is_same<T, long double>::value) *fp++ = 'L';
  switch (specs.format) {
  case float_format::hex:
    *fp++ = specs.upper ? 'A' : 'a';
    break;
  case float_format::fixed:
    *fp++ = 'f';
    break;
  default:
    *fp++ = 'e';
    break;
  }
  *fp = '\0';

  int printf_precision = precision;
  if (specs.format == float_format::general || specs.format == float_format::exp)
    printf_precision = precision < 0 ? 5 : precision - 1;
  if (printf_precision < 0 && specs.format != float_format::general &&
      specs.format != float_format::exp)
    printf_precision = -1;

  size_t offset = buf.size();
  int n;
  for (;;) {
    size_t capacity = buf.capacity() - offset;
    n = FMT_SNPRINTF(buf.data() + offset, capacity, format, printf_precision,
                     value);
    if (n < 0) {
      buf.reserve(buf.capacity() + 1);
      continue;
    }
    if (to_unsigned(n) >= capacity) {
      buf.reserve(offset + to_unsigned(n) + 1);
      continue;
    }
    break;
  }
  size_t size = to_unsigned(n);
  char* begin = buf.data() + offset;

  if (specs.format == float_format::hex) {
    buf.resize(offset + size);
    return 0;
  }

  if (specs.format == float_format::fixed) {
    if (printf_precision == 0) {
      buf.resize(offset + size);
      return 0;
    }
    char* point = static_cast<char*>(std::memchr(begin, '.', size));
    if (!point) {
      buf.resize(offset + size);
      return 0;
    }
    int frac = static_cast<int>(begin + size - point - 1);
    std::memmove(point, point + 1, to_unsigned(frac));
    buf.resize(offset + size - 1);
    return -frac;
  }

  // Exponent format: d[.ddd]e(+|-)XX
  char* e = begin + size;
  while (e != begin && *e != 'e' && *e != 'E') --e;
  int exp_value = 0;
  {
    const char* p = e + 1;
    bool neg = false;
    if (*p == '-') {
      neg = true;
      ++p;
    } else if (*p == '+') {
      ++p;
    }
    while (p != begin + size) exp_value = exp_value * 10 + (*p++ - '0');
    if (neg) exp_value = -exp_value;
  }
  // Fractional digits are between the point (if any) and e.
  int num_frac = 0;
  if (e - begin > 1 && begin[1] == '.') {
    num_frac = static_cast<int>(e - begin) - 2;
    if (num_frac > 0) std::memmove(begin + 1, begin + 2, to_unsigned(num_frac));
  }
  while (num_frac > 0 && begin[num_frac] == '0') --num_frac;
  buf.resize(offset + 1 + to_unsigned(num_frac));
  return exp_value - num_frac;
}
```
