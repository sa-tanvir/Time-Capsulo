Line: width TAB side TAB name_length TAB name_seed (the name text is synthesised from length+seed by the driver). Name lengths up to 20 (S), 200 (M), 2000 (L); 400 / 6000 / 20000 cases.
Driver constructs `name_formatter(padding_info)` and calls `format(msg, tm, buf)`; the buffer is hashed.
