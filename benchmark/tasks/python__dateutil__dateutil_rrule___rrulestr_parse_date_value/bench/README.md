Workload: generated DTSTART/EXDATE values (comma lists of basic, date-only, ISO, Z/offset/named-zone
date strings), random VALUE=/TZID= parameter lists and rule_tzids maps, plus fixed error cases in S
(unsupported/duplicate parms, TZID+aware date, bad tzids, raising tzids callable, unparsable dates).
Dates per case grow ~10x per size (<=10/100/1000). The driver calls
`rrulestr._parse_date_value(...)` directly with fixed tzoffset-based tzids (mapping or callable) and
tzinfos={"Z": tzutc(), ...}; check mode hashes repr of the returned lists or exception type+message.
