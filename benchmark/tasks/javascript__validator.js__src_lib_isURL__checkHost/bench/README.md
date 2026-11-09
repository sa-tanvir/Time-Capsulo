Calls the module-private `checkHost(host, matches)` directly: the driver transpiles `/w/src/lib/isURL.js` with the repo's Babel config plus one line exporting the helper.
Workload: random dotted host names checked against lists mixing exact host strings (~85%) and regular expressions (suffix, prefix, anchored, case-insensitive); ~30% of hosts are taken from their list, some are upper-cased.
S additionally holds the whitelist/blacklist examples of the test suite, an empty list and IPv6 hosts.
Sizing: list length ~10 / ~100 / ~1000 entries (S/M/L), 300 cases each.
