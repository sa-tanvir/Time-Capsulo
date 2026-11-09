# Functional specification

## 1. Component overview

`relativedelta.__add__(other)` implements `relativedelta + X` (and, through `__radd__`, `X + relativedelta`; subtraction from a date is implemented as adding the negated delta). A `relativedelta` holds *relative* quantities (plural names: `years`, `months`, `days`, `leapdays`, `hours`, `minutes`, `seconds`, `microseconds`), *absolute* replacements (singular names: `year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond`, each `None` when unset) and an optional `weekday` (a `weekday` object such as `MO`, `FR(-1)`). See context.md for the attributes and constructor. The method supports three kinds of right operand and returns `NotImplemented` for everything else.

## 2. Functional requirements

**A. `other` is a `relativedelta`** — return a new object of the *same class as `self`* (subclasses are preserved) built through the constructor, so the usual normalisation (e.g. 25 hours → 1 day 1 hour, 13 months → 1 year 1 month) applies:
- each relative field is the sum of both operands' fields;
- `leapdays` is `other.leapdays` if it is non-zero, otherwise `self.leapdays`;
- each absolute field and `weekday`: `other`'s value if it is not `None`, otherwise `self`'s.
Example: `relativedelta(days=10) + relativedelta(years=1, months=2, days=3, hours=4, minutes=5, microseconds=6)` == `relativedelta(years=1, months=2, days=13, hours=4, minutes=5, microseconds=6)`; `relativedelta() + relativedelta(day=0, hour=0)` == `relativedelta(day=0, hour=0)` and vice versa.

**B. `other` is a `datetime.timedelta`** — return a new object of `self`'s class with the timedelta's `days`, `seconds` and `microseconds` added to `self.days`, `self.seconds`, `self.microseconds` (then normalised by the constructor); all other fields, including absolute ones, weekday and leapdays, copied from `self`. Example: `relativedelta() + timedelta(weeks=1, days=1, hours=1, minutes=1, seconds=1, milliseconds=1, microseconds=1)` == `relativedelta(weeks=1, days=1, hours=1, minutes=1, seconds=1, microseconds=1001)`.

**C. `other` is a `datetime.date` or `datetime.datetime`** — compute a new date/datetime:
1. If `self` carries any time information (`self._has_time` true) and `other` is a plain `date`, first convert it to a `datetime` at midnight of that day (the result is then a `datetime`).
2. Year: the absolute `year` if set (truthy) else `other.year`, plus `years`.
3. Month: the absolute `month` if set else `other.month`, plus `months` (|months| ≤ 11 after normalisation); if the result leaves 1..12 it wraps around by one year (13 → January of next year, 0 → December of previous year).
4. Day: the absolute `day` if set else `other.day`, clipped to the number of days of the resulting month/year (Jan 31 + 1 month → Feb 28/29).
5. Absolute `hour`, `minute`, `second`, `microsecond` that are not `None` replace those fields. All replacements in steps 2–5 are applied together to `other` (keeping its tzinfo and other fields).
6. Then add the relative `days`, `hours`, `minutes`, `seconds`, `microseconds` as a timedelta (floats allowed: `days=0.5` adds 12 hours). If `leapdays` is non-zero, the resulting month (from step 3) is after February and that year is a leap year, `leapdays` is added to the days.
7. Finally, if `weekday` is set with weekday index *w* (0 = Monday) and count *n* (`None` or 0 means +1): for *n* > 0 move forward to the *n*-th date whose weekday is *w*, counting the current date as the first if it already matches; for *n* < 0 move backward analogously. E.g. Wed 2003-09-17 + `relativedelta(weekday=WE)` → same day; + `relativedelta(weekday=FR)` → 2003-09-19; + `relativedelta(days=+1, weekday=WE(+1))` → 2003-09-24; `date(2003,1,1) + relativedelta(day=4, weeks=+14, weekday=MO(-1))` → `date(2003,4,7)`.

**D. Anything else** — return `NotImplemented` (so `relativedelta(days=3) + 9` raises `TypeError`, and a foreign object defining `__radd__` gets to handle the operation).

## 3. Input specification

- `self`: a (possibly subclassed) `relativedelta` that has already been normalised by its constructor; numeric fields may be `int` or `float`.
- `other`: any object.

## 4. Output specification

- Case A/B: a new instance of `type(self)`; neither operand is modified.
- Case C: a `date` when `other` is a `date` and `self` has no time component, otherwise a `datetime` (same tzinfo as `other`).
- Case D: the `NotImplemented` singleton.

More examples: `datetime(2000,1,1) + relativedelta(days=1)` → `datetime(2000,1,2)`; `date(2003,1,31) + relativedelta(months=+1)` → `date(2003,2,28)`; `date(2003,9,17) + relativedelta(months=+1, weeks=+1, hour=10)` → `datetime(2003,10,24,10,0)`; `date(2000,1,1) + relativedelta(yearday=260)` (month 9, day 16, leapdays −1) → `date(2000,9,16)`; `date(2003,1,1) + relativedelta(nlyearday=260)` → `date(2003,9,17)`; `datetime(2000,1,1) + relativedelta(months=float(1))` → `datetime(2000,2,1)`.

## 5. Edge cases and constraints

- Absolute `year`/`month`/`day` equal to 0 are treated as unset in case C.
- Errors from building the new date (e.g. year outside 1..9999 → `ValueError`, overflow in the timedelta step → `OverflowError`) propagate.
- The weekday step is applied last, after all other arithmetic; a weekday with `n` of `None`/0/1 never moves backwards.
- No mutation of `self` or `other`.
