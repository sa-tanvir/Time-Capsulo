Workload: seeded command trees shaped as root -> 0-2 intermediate commands -> target, where the target
has many children (runnable/hidden/deprecated/help-topic, some aliases) and many flags (string/bool/int/
slice, local or persistent, some hidden or deprecated) and ancestors add (persistent) flags; plus header
fields (section, title, manual, source, fixed date) and DisableAutoGenTag on some nodes.
S = 400 cases (<= 3 children/flags); M = 60 (<= 30); L = 8 (<= 300). The driver (Go test in package `doc`)
builds trees and completes headers with `fillHeader` before timing, then calls `genMan(cmd, header)`.
