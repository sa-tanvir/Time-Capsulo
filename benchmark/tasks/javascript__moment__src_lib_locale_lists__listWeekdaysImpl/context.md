# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/locale/lists.js`

## Imports / includes available in this file

```
import isNumber from '../utils/is-number';
import { getLocale } from './locales';
import { createUTC } from '../create/utc';
```

## Other functions defined in the same file (signatures only; you may call them)

```
get ( format , index , field , setter )
listMonths ( format , index )
listMonthsImpl ( format , index , field )
listMonthsShort ( format , index )
listWeekdays ( localeSorted , format , index )
listWeekdaysMin ( localeSorted , format , index )
listWeekdaysShort ( localeSorted , format , index )
```

## Behaviour of the imported helpers and of `get`

- `isNumber(x)`: `true` for primitive numbers (including `NaN`) and `Number` objects.
- `getLocale()` (no argument): the current global `Locale` object (the one selected with
  `moment.locale(...)`). Its first day of the week is `locale._week.dow` (also returned by
  `locale.firstDayOfWeek()`), an integer 0–6 (0 = Sunday).
- `createUTC()`: a new moment in UTC mode for the current instant.
- `get(format, index, field, setter)` (same file): creates a UTC moment, sets its unit `setter`
  (here `'day'`, the day of the week) to `index`, and returns
  `getLocale()[field](thatMoment, format)`, i.e. the name of that weekday as given by the global
  locale's `weekdays`/`weekdaysShort`/`weekdaysMin` method for the given format string. Setting
  the day of the week to an integer outside 0–6 moves to another week, so the name returned is
  that of weekday `index` modulo 7 (e.g. `-1` → Saturday, `9` → Tuesday). If `index` is `NaN`, the day is left unchanged, so the
  name returned is that of the current UTC date's weekday.
- The public wrappers call it as `listWeekdays(a, b, c)` → `listWeekdaysImpl(a, b, c, 'weekdays')`,
  `listWeekdaysShort` → field `'weekdaysShort'`, `listWeekdaysMin` → field `'weekdaysMin'`. These
  back `moment.weekdays(...)`, `moment.weekdaysShort(...)` and `moment.weekdaysMin(...)`.
