Workload: key/value pair lists for Route.Queries (literal, empty and {var}/{var:pattern} values) on fresh
routes with optional host/path templates; some odd counts, duplicate variables, malformed templates, pre-existing errors.
Pairs per call: 2 (S), 20 (M), 200 (L). Queries mutates the route, so fresh route copies are made outside the timed region.
