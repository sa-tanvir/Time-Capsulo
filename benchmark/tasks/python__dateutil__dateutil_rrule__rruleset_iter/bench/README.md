Workload: generated rrulesets on an hourly grid from 2000-01-01 (HOURLY/DAILY/WEEKLY rules with
COUNT, optional byhour; shuffled rdates/exdates with many collisions; optional exrules), plus fixed
edge cases in S (empty set, only exclusions, duplicate rdates, everything excluded). Occurrences per
set grow ~10x per size (~100/1000/10000). The driver builds fresh rruleset(cache=False) objects
outside the timed region and times `list(rset._iter())`; check mode hashes the outputs and `_len`.
