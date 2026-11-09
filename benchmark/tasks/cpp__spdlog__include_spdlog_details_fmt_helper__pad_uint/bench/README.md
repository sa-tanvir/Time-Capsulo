Line: type TAB value TAB width (type 0/1/2 = unsigned short / uint32_t / uint64_t; width 0..20). S: boundary grid + 150 random; M: 30000; L: 300000 cases with wider values.
Driver instantiates `fmt_helper::pad_uint<T>` for the three types; check mode hashes the appended text.
