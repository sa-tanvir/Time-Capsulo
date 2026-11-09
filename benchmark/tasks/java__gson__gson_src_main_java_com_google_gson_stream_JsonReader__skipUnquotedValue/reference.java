private void skipUnquotedValue() throws IOException {
  do {
    int i = 0;
    for (; pos + i < limit; i++) {
      switch (buffer[pos + i]) {
      case '/':
      case '\\':
      case ';':
      case '#':
      case '=':
        checkLenient(); // fall-through
      case '{':
      case '}':
      case '[':
      case ']':
      case ':':
      case ',':
      case ' ':
      case '\t':
      case '\f':
      case '\r':
      case '\n':
        pos += i;
        return;
      }
    }
    pos += i;
  } while (fillBuffer(1));
}
