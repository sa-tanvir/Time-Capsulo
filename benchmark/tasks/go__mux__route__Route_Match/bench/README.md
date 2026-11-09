Workload: (route, request, initial RouteMatch state) triples: methods, schemes, headers, header regexps,
host/path/query templates, subrouters, strict slash, build-only/erroneous routes; ~20% mismatches. Variables per
route: 3 (S), 30 (M), 300 (L). The driver calls `route.Match(req, &m)` and hashes ok/MatchErr/Route/Vars/handler output.
