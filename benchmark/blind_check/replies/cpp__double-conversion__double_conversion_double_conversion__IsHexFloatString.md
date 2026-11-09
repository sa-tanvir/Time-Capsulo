```cpp
static bool IsHexFloatString(Iterator start,
                             Iterator end,
                             uc16 separator,
                             bool allow_trailing_junk) {
  Iterator current = start;
  bool saw_digit = false;
  while (isDigit(*current, 16)) {
    saw_digit = true;
    if (Advance(&current, separator, 16, end)) return false;
  }
  if (*current == '.') {
    if (Advance(&current, separator, 16, end)) return false;
    while (isDigit(*current, 16)) {
      saw_digit = true;
      if (Advance(&current, separator, 16, end)) return false;
    }
  }
  if (!saw_digit) return false;
  if (*current != 'p' && *current != 'P') return false;
  if (Advance(&current, separator, 16, end)) return false;
  if (*current == '+' || *current == '-') {
    if (Advance(&current, separator, 16, end)) return false;
  }
  if (!isDigit(*current, 10)) return false;
  while (isDigit(*current, 10)) {
    if (Advance(&current, separator, 16, end)) return true;
  }
  if (allow_trailing_junk) return true;
  return !AdvanceToNonspace(&current, end);
}
```
