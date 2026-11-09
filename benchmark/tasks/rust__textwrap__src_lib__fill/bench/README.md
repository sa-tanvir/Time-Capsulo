Workload: (width, break_words, initial_indent, subsequent_indent, text) cases. S holds the literal cases from the
test suite/docs plus short random texts; M ~300-800 words, L ~3000-8000 words per case: hyphenated words, flags,
NBSP / non-breaking hyphens, wide CJK/fullwidth characters, runs of spaces and embedded newlines; widths 0..120 and
usize::MAX. break_words=false cases are ASCII-only (the 2018 wrapping iterator panics on some multibyte input then).
Invocation: `driver.rs` is appended to `src/lib.rs` of a container-local copy (`/tmp/w`) as `mod tc_bench`, builds one
`Wrapper::new(w).initial_indent(..).subsequent_indent(..).break_words(..)` per case before timing, and times `fill`.
