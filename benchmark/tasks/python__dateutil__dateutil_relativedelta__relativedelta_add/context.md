# Context for the function to implement

- **Language:** python
- **File:** `dateutil/relativedelta.py`
- **Enclosing scope:** `class relativedelta(object)`

## Imports / includes available in this file

```
import datetime
import calendar
import operator
from math import copysign
from six import integer_types
from warnings import warn
from ._common import weekday
```

## Other functions defined in the same file (signatures only; you may call them)

```
_fix( self )
_set_months( self , months )
_sign( x )
normalized( self )
weeks( self )
weeks( self , value )
```

## Instance state and other members of the enclosing class (you may rely on them)

Attributes of every `relativedelta` instance (set by `__init__`, then normalised by `_fix()`):

- Relative (numbers, default 0): `years` (int), `months` (int, |months| <= 11 after `_fix`),
  `days` (weeks are folded into days), `leapdays`, `hours`, `minutes`, `seconds`, `microseconds`.
  `days/hours/minutes/seconds/microseconds` may be floats.
- Absolute (default `None`): `year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond`.
- `weekday`: `None` or a `dateutil._common.weekday` instance (attributes `weekday` = 0..6 with
  0=Monday, and `n` = `None` or a non-zero/zero int count; `MO(+2)`, `FR(-1)` etc.; integers passed to
  the constructor are converted to `weekday` objects). Weekday objects are always truthy.
- `_has_time`: 1 if any of `hours`, `minutes`, `seconds`, `microseconds` is non-zero or any of
  `hour`, `minute`, `second`, `microsecond` is not `None`, else 0.

Constructor (keyword form):

```
relativedelta(dt1=None, dt2=None,
              years=0, months=0, days=0, leapdays=0, weeks=0,
              hours=0, minutes=0, seconds=0, microseconds=0,
              year=None, month=None, day=None, weekday=None,
              yearday=None, nlyearday=None,
              hour=None, minute=None, second=None, microsecond=None)
```

It stores the values above (`days = days + weeks * 7`; `yearday`/`nlyearday` are converted to
`month`/`day` and, for `yearday > 59`, `leapdays = -1`) and calls `self._fix()`.

`_fix(self)`: carries overflow upward keeping signs: |microseconds| > 999999 into seconds,
|seconds| > 59 into minutes, |minutes| > 59 into hours, |hours| > 23 into days, |months| > 11 into
years; then recomputes `_has_time`.

`normalized(self)`: returns an equivalent instance with integer relative fields (fractions cascaded
downward). `__radd__(self, other)` returns `self.__add__(other)`; `__rsub__(self, other)` returns
`self.__neg__().__radd__(other)`; `__neg__` negates the relative fields and keeps the others.

Module-level: `MO, TU, WE, TH, FR, SA, SU = weekdays` (weekday objects with `n=None`);
`calendar` and `datetime` modules are imported.
