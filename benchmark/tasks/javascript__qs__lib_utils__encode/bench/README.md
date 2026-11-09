Calls the exported `require('/w/lib/utils.js').encode(str, encode, charset)` directly, once per case.
Workload: strings mixing unreserved ASCII, reserved/punctuation, Latin-1, BMP (incl. private use) and astral
characters, repeated `rep` times by the driver to reach long inputs, under charset utf-8, iso-8859-1 or undefined.
S additionally holds the test-suite strings, lone surrogates, numbers, booleans, Buffers (incl. empty) and Symbols.
Sizing: mean input length ~90 / ~900 / ~10000 characters (S/M/L), 300 random cases each.
