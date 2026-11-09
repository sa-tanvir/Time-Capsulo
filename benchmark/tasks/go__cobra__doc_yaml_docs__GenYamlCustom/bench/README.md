Workload: seeded command trees shaped as root -> 0-2 intermediate commands -> target, where the target has
many children (runnable/hidden/deprecated/help-topic) and many flags (string/bool/int/slice, local or
persistent, some hidden/deprecated, texts with quotes, colons, non-ASCII, some > 60 bytes) and ancestors add
(persistent) flags. S = 300 cases (<= 3 children/flags); M = 40 (<= 30); L = 6 (<= 300). The driver (Go test
in package `doc`) builds the trees before timing and calls `GenYamlCustom(cmd, buf, identity)` into a reset
`bytes.Buffer`; check mode hashes the YAML text.
