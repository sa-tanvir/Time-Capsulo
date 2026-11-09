Workload: 300 seeded constructor calls per size, each passing a random subset of method/url/headers/files/data/params/
auth/cookies/json (sometimes falsy values) and hooks: none, an unsupported event (ValueError), a single callable, or a
list/tuple of up to 10 (S) / 100 (M) / 1000 (L) hooks with ~15% non-callables. The driver calls `Request(**kwargs)` and
hashes stored attributes (repr and identity with the inputs), registered hook ids, hook-list sharing and attribute names.
