Line: width TAB side TAB level(0..6). S: all width x side x level combinations + 100 random; M: 30000; L: 300000 cases.
Driver constructs `level_formatter(padding_info)` and calls `format(msg, tm, buf)`; the buffer is hashed.
