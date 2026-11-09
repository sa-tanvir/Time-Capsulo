Workload: a seeded pool of relativedeltas (relative fields incl. some floats, absolute fields,
weekday(n), leapdays, yearday/nlyearday) and a pool of right operands (relativedelta, timedelta,
date, naive/tz-aware datetime, unsupported int/str/None); cases are index pairs, S/M/L =
2k/20k/200k additions. Objects are built outside the timed region (no mutation by `__add__`);
the driver times `rd.__add__(other)` and check mode hashes type+repr of each result.
