First line: escaped text built from a random vocabulary of words (1-20 letters). Then lines 'start count reps': 80% exact word ranges (cache hits and collisions), others random ranges, empty and negative counts; reps=2 asks twice in a row and the digest records whether the second result is the same instance (S) or just equal (D).
The private static cacheString is called through a static-final MethodHandle with a fresh 512-slot cache. S/M/L: 80 / 20,000 / 300,000 calls.
TCBench.java is in the target's package, compiled against target/classes into /tmp/tcb; /w is never modified.
