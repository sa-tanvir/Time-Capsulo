Workload: 300 seeded Link-header strings per size with up to 4 (S) / 40 (M) / 400 (L) links. Links vary in URL
quoting (<...>, spaces, quotes, bare), separators (",", ", ", " , "), and parameters (plain, quoted, padded, empty
pieces, double '=', missing '='); ~3% are empty/blank headers. The driver calls `parse_header_links(value)` and
hashes the ordered items of every returned dict.
