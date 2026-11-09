Workload: 40 seeded cookie jars per size with 10 (S) / 100 (M) / 1000 (L) cookies (names drawn from a pool of n/2 so
duplicates are common; mixed domains, paths, empty and non-empty values) and 20 lookups each (name with optional
domain/path filters, ~15% unknown names). Jars are built untimed; the driver times
`jar._find_no_duplicates(name, domain, path)` and hashes each value or exception type/args, plus the jar contents.
