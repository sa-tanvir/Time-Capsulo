Workload: seeded (quantity, singular, plural) triples, 6k per size. Words are random letters
(including upper-case vowels) with endings chosen to hit every rule (s/sh/tch/ch/x, vowel or
consonant + o/y, upper-case endings), ~10% explicit plurals and ~3% special technical words.
S adds fixed edge cases from the tests; word length is 1-12 (S), 12-120 (M), 120-1,200 (L).
The driver is a Go test (`TestTCBench`) copied into package `english`; it calls
`PluralWord` directly and hashes the quoted results (check) or times the calls (time).
