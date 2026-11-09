Workload: seeded host/path/prefix/query templates with default and custom variable patterns plus value maps
(mostly valid; some missing or invalid values, extra keys, strict slash, query escaping). Variables per template:
2 (S), 20 (M), 200 (L). Templates are compiled with newRouteRegexp before timing; the driver calls `rr.url(values)`.
