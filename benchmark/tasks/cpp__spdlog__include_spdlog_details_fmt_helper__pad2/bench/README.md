One int per line. S: boundary values (0..124, 999.., negatives, INT_MIN/MAX) + 300 random; M: 30000 values up to 1e7; L: 300000 values over the full int range.
Driver calls `fmt_helper::pad2(n, fmt::memory_buffer&)` and hashes the buffer text; time mode reuses one buffer.
