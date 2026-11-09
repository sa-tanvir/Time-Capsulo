Workload: routes with host/path/prefix/query templates, schemes and optional BuildVarsFunc, plus variable
pairs (mostly valid; some missing/odd/invalid). Variables per route: 3 (S), 30 (M), 300 (L).
Routes are built before timing; the driver calls `route.URL(pairs...)` and hashes the URL fields or the error.
