One path per line. S: 33 hand-written edge cases + 250 short random paths (<30 chars); M: 1500 paths of 100-400 chars; L: 1000 paths of 1000-4000 chars (more dots/separators, so the scan distance grows).
Driver calls `file_helper::split_by_extension(path)` directly (static public member) and hashes base + 0x01 + extension.
Check mode hashes the concatenated results; time mode only keeps a length checksum.
