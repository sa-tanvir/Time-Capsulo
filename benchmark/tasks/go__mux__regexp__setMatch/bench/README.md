Workload: matching (route, request) pairs: host/path/query variables, strict-slash redirects, encoded paths,
relative requests with req.Host. Variables per route: 3 (S), 30 (M), 300 (L); S starts with test-suite cases.
The driver calls `route.regexp.setMatch(req, &m, route)`; check mode hashes Vars and runs any redirect handler.
