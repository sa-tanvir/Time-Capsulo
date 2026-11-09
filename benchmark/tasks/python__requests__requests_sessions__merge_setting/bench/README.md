Workload: 200 seeded (request, session, dict_class) cases per size. Each side is None (8%), a scalar (6%) or an
OrderedDict/dict with up to 10 (S) / 100 (M) / 1000 (L) header-like keys (20% upper-cased variants, 15% None values).
dict_class is the default, OrderedDict, CaseInsensitiveDict or dict. Inputs are not mutated, so they are built once.
The driver calls `merge_setting(req, ses[, dict_class=...])` and hashes result identity, type and items, plus an input-unchanged flag.
