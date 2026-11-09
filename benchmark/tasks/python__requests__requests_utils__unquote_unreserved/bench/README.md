Workload: 300 seeded URIs per size with up to 60 (S) / 600 (M) / 6000 (L) tokens: plain characters, random hex
escapes in mixed case (unreserved, reserved and non-ASCII bytes), malformed escapes kept literally ("%-", "%/", "% ",
"%4-", "%.x", trailing "%"), and in ~10% of URIs alphanumeric non-hex escapes ("%zz", "%é1") that raise InvalidURL.
The driver calls `unquote_unreserved(uri)` and hashes the result or the exception type and message.
