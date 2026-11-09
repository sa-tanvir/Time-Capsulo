Workload: seeded lists of 0-4 date components (2/4-digit years, months, days, some 4-entry error cases),
with optional M/D/Y labels and random yearfirst/dayfirst flags; S/M/L = 2k/20k/200k objects.
The driver builds `_ymd` objects via `append(value, label)` outside the timed region (rebuilt each
repeat) and times only `resolve_ymd(yearfirst, dayfirst)`; check mode hashes every result tuple or
exception type+message.
