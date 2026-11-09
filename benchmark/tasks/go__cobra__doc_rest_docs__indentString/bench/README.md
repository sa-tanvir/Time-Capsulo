Workload: seeded `[s, p]` pairs. Texts are random word/newline mixes (including blank lines,
multi-byte UTF-8, `\r`), prefixes vary ("  ", "\t", "> ", "", ...). S = 2000 texts of ~60 bytes
plus fixed edge cases; M = 200 texts of ~6 KB; L = 20 texts of ~120 KB.
The driver is a Go test (`TestTCBench`) copied into package `doc`; it calls `indentString(s, p)`
directly and hashes the quoted results (check) or times the calls (time).
