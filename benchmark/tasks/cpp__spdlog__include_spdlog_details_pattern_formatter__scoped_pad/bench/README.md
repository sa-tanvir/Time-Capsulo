Line: width TAB side(l|r|c) TAB text_length. S: grid of widths x lengths x sides + 100 random; M: 30000; L: 300000 cases.
Driver builds a `padding_info`, constructs `scoped_pad(size_t, padinfo, buffer)`, appends a synthetic text of the given length, lets the object die and appends '#'; the whole buffer is hashed.
