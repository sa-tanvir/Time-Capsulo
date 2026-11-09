Pairs of strings over a small alphabet (mutated copies and unrelated strings). The driver builds the full Levenshtein cost matrix for each pair (shorter string first, as the library does) outside the timed region, then calls the private static findDetailedResults via reflection and hashes the returned LevenshteinResults.toString().
In time mode each pair is processed several times per repeat (more at larger sizes) because a single back-trace is very cheap.
TCBench.java lives in the same package as the target and is compiled against target/classes and commons-lang3 into /tmp/tcb.
