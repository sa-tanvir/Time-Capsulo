Workload: seeded non-empty integer lists over small alphabets (S: up to 300 items, M: 4k, L: 40k),
window sizes 1-6, predicates = set membership (w=1), exact pattern match, or first-item match (w>1),
0-4 substitutes and count in {None, 0, 1, 3, 50}.
The driver calls list(replace(seq, pred, subs, count=..., window_size=...)); check mode hashes repr() of each output.
