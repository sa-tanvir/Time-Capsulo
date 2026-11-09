Workload: seeded dispatch cases: key 'response' (or an unregistered key), registry None / {} / single callable /
list / tuple / empty list (sometimes with an extra event entry), chains of up to K small integer hooks (some
returning None or 0, one using the forwarded `step` kwarg; rare raising hooks in S), K = 4 (S), 40 (M), 400 (L).
Registries are built before timing; the driver calls `dispatch_hook(key, hooks, data, **kwargs)` per case and
hashes the result (or the ValueError message).
