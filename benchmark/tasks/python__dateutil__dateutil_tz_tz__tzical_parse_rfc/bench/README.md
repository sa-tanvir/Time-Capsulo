Workload: 40 seeded iCalendar texts per size with 1 (S), 10 (M) or 100 (L) VTIMEZONE blocks, each with 1-3
STANDARD/DAYLIGHT components (DTSTART with/without VALUE=DATE-TIME, RRULE incl. UNTIL, RDATE, EXDATE, offsets
with seconds, TZNAME, COMMENT), optional VCALENDAR wrapper, CRLF/LF endings, folded and blank lines. S also
holds ~30 hand-written cases covering every ValueError path. The driver calls `_parse_rfc(s)` on a fresh
`tzical` (built via `__new__`, outside the timed region); the digest covers the error type/message and, per
TZID, each component's offsets, isdst, tzname and its first 6 recurrence instants.
