Workload: 200 strings per size; S starts with ~26 edge cases from the tests (failures, fuzzy tokens, AM/PM, tz forms).
Remaining cases embed a random date/time core (ISO, compact, ctime, named months, h/m/s, AM/PM, tz names/offsets) in filler:
jump words for strict cases, free text for fuzzy/fuzzy_with_tokens cases; filler grows 2 -> 40 -> 400 words (S/M/L).
Driver calls `parser(info)._parse(s, dayfirst=..., yearfirst=..., fuzzy=..., fuzzy_with_tokens=...)` directly; the parserinfo
has `_year`/`_century` pinned to 2019/2000 so two-digit years do not depend on the host clock.
check hashes repr(result) + century_specified + skipped tokens ((None, None) for failures).
