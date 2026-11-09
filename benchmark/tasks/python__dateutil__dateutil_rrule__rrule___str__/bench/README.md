Workload: seeded `rrule` constructor arguments: all seven frequencies, intervals, optional wkst, COUNT or UNTIL,
naive or UTC-aware dtstart (1970-2100), and random subsets of BYSETPOS/BYMONTH/BYMONTHDAY/BYYEARDAY/BYWEEKNO/
BYDAY (plain and nth weekdays)/BYHOUR/BYMINUTE/BYSECOND/BYEASTER with up to K values each, K = 3 (S), 30 (M),
300 (L). Rules are constructed before timing; the driver calls `str(rule)` (twice per rule in check mode, to
detect mutation) and hashes the strings.
