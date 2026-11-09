Workload: query templates (and a few non-query templates) with request query strings of 3 (S), 30 (M)
or 300 (L) parameters: repeated keys, encoded characters, missing keys. Requests are built before timing;
the driver calls `rr.getURLQuery(req)` (which parses the query each call).
