Calls the module-private `isValidDate(str)` directly: the driver transpiles `/w/src/lib/isISO8601.js` with the repo's Babel config plus one line exporting the helper.
Workload: strings that all satisfy the module's ISO 8601 pattern (the helper's precondition), years 1000-9999: calendar dates (extended/basic, incl. day 29-31 overflow), ordinal dates (days near 365/366, leap/century years), week dates, year-month, with optional times, fractions, zones and year signs.
S additionally holds the test-suite strings and leap-year boundary cases.
Per-call input size is bounded by the format, so S/M/L scale the case count: 2,000 / 20,000 / 200,000 cases.
