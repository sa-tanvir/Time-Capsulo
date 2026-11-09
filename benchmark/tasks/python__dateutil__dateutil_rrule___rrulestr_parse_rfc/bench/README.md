Workload: generated RFC 5545 recurrence texts (DTSTART/RRULE/RDATE/EXRULE/EXDATE lines, folded
lines, lower-case variants, TZID-qualified dates, forceset/compatible/unfold/ignoretz/cache flags)
plus fixed error cases in S. Per-case date entries grow ~10x per size (<=10/100/1000).
The driver calls `rrulestr._parse_rfc(s, tzids=<fixed tzoffset mapping>, tzinfos={"Z": tzutc()}, ...)`;
only the parse call is timed. Check mode hashes the result type, str() of the contained rules and
the first 15 occurrences (or exception type+message).
