static bool IsHexFloatString(Iterator start,
                             Iterator end,
                             uc16 separator,
                             bool allow_trailing_junk) {
  ASSERT(start != end);

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
  if (Advance(&current, separator, 16, end)) return true;
  while (isDigit(*current, 10)) {
    if (Advance(&current, separator, 16, end)) return true;
  }
  return allow_trailing_junk || !AdvanceToNonspace(&current, end);
}
