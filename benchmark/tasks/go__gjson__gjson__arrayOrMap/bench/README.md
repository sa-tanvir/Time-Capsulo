Workload: seeded `[Raw, vc, valueize]` cases; random JSON objects/arrays (`json.dumps` compact / spaced /
indented, ASCII-escaped or raw UTF-8, nested containers, escaped strings, numbers, literals), 20% with leading
whitespace; vc = 0 (40%), the matching bracket (55%) or the wrong one (5%); valueize 50/50. S adds 25
hand-written documents x 3 vc x 2 valueize. Approx. bytes per document: ~150 (S), ~1.5 KB (M), ~15 KB (L).
Driver: Go test in package `gjson`; calls `Result{Type: JSON, Raw: raw}.arrayOrMap(vc, valueize)`, hashes all fields.
