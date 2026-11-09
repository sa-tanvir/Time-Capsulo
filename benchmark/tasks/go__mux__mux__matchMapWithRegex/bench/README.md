Workload: like matchMapWithString but values are regexp sources (anchored, substring, alternations) or
null (nil regexp = presence only); patterns are compiled before timing. Entries per toCheck: 3/30/300 (S/M/L).
S starts with the ExampleRoute_HeadersRegexp and TestHeaders cases. Driver calls `matchMapWithRegex` directly.
