Workload: seeded ISO-8601 time strings (hh, hhmm, hh:mm, hhmmss, hh:mm:ss with ./, fractions of
1-12 digits, Z/z/±HH/±HHMM/±HH:MM zones, 24:00 midnight) plus ~8% invalid strings with specified
errors (too short, unused components, bad zones, 24 not at midnight); S/M/L = 2k/20k/200k strings.
The driver encodes to bytes outside the timed region and times `isoparser()._parse_isotime(b)`;
check mode hashes each result list repr or exception type+message.
