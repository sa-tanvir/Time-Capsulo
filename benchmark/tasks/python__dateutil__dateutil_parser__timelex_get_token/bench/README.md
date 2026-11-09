Workload: 300 seeded strings per size; S also contains ~45 hand-picked edge cases (dotted/comma numbers,
NULs, whitespace variants, quirky letter/digit mixes). Each string joins 4 (S), 40 (M) or 400 (L) random
date-like pieces (words, integers, decimals with '.' or ',', times, `Word.DD.YYYY`, ISO stamps, random
`ab1.,` noise) with random separators. The driver builds fresh `_timelex(s)` objects outside the timed
region, then calls `get_token()` until it returns None; the digest covers every token list plus a final call.
