You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `listWeekdaysImpl(localeSorted, format, index, field)` in `src/lib/locale/lists.js`

## 1. Component overview

Module-private implementation behind `moment.weekdays()`, `moment.weekdaysShort()` and
`moment.weekdaysMin()`. It returns either the list of the seven weekday names of the current
global locale, or a single weekday name, optionally ordered so that the locale's first day of the
week comes first, and optionally for a specific format string (some locales use different word
forms inside a format). `field` selects which locale method produces the names: `'weekdays'`,
`'weekdaysShort'` or `'weekdaysMin'`.

## 2. Functional requirements

Callers use the shapes `()`, `(index)`, `(true|false)`, `(bool, index)`, `(bool, format)` and
`(bool, format, index)`. A format string is only honoured after a boolean first argument; a
non-boolean first argument is always taken as the index (see rule 1 for what `(format)` gives).

1. **Argument normalisation.**
   - If `localeSorted` is a boolean: when `format` is a number, it is really the index
     (`index = format`, no format). The format string is `format`, or `''` if it is falsy/absent.
   - Otherwise (first argument not a boolean) the second and third parameters are **ignored**:
     the index is the first argument's value **as is** (even when it is a string), sorting is
     off, and the format is the first argument if it is a non-number truthy value, else `''`.
     Thus `(2)` asks for weekday 2; `()`, `(undefined)` and `(null)` ask for the list; a string
     such as `('dddd')`, `('3')` or `('')` asks for a single name (rule 3).
2. **Shift.** If sorting is on (`localeSorted === true`) the shift is the global locale's first day
   of the week (`getLocale()._week.dow`), otherwise `0`.
3. **Single name.** If the index is not `null`/`undefined`, return one name: the weekday number
   is `(index + shift) % 7` evaluated with JavaScript's `+` and `%` operators. For a string
   index this concatenates: `'3'` gives `'30' % 7` = 2, `''` gives `'0' % 7` = 0, and `'dddd'`
   gives `NaN` (for which `get` returns the name of the current UTC day's weekday, see
   `context.md`); the name is
   obtained from the helper `get` (see `context.md`) with that weekday number, the normalised
   format string, `field`, and the setter `'day'`.
4. **Full list.** Otherwise return a new array of 7 names; position `i` (0–6) holds the name of
   weekday number "i plus shift, modulo 7", obtained from `get` in the same way.

The names always come from the **global** locale at call time.

## 3. Input specification

- `localeSorted`: boolean, number, string, `null` or `undefined` (see the shapes above).
- `format`: a moment format string (e.g. `'dddd'`, `'[On] dddd'`), a number (index), or absent.
- `index`: an integer (normally 0–6; other integers are allowed and wrap as described in
  `context.md`), or absent.
- `field`: `'weekdays'`, `'weekdaysShort'` or `'weekdaysMin'`.

## 4. Output specification

A string (single name) or an array of 7 strings. Examples for the default English locale
(week starts on Sunday, `dow = 0`):

- `listWeekdaysImpl(undefined, undefined, undefined, 'weekdays')` →
  `['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']`
- field `'weekdaysShort'`, no arguments → `['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']`;
  `'weekdaysMin'` → `['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']`
- `(0, …, 'weekdays')` → `'Sunday'`; `(2, …, 'weekdaysShort')` → `'Tue'`; `(-1, …)` → `'Saturday'`
- `('3')` → `'Tuesday'`; `('')` → `'Sunday'`; `('dddd')` and `('dddd', 2)` → today's weekday name
  (e.g. `'Monday'` on 2019-01-21)

With a custom global locale whose weekdays are `one … seven` (short `on … se`, min `1 … 7`) and
whose week starts on Wednesday (`dow = 3`):

- `(true)` with `'weekdays'` → `['four', 'five', 'six', 'seven', 'one', 'two', 'three']`
- `(true, 0)` → `'four'`; with `'weekdaysMin'` → `'4'`
- `(false, 2)` → `'three'`; `(2)` → `'three'`; `(0)` → `'one'`
- `(true, 'dddd', 2)` → `'six'`

For a locale whose full weekday names depend on the format, `(true, '[On] dddd')` returns the
names the locale gives for that format string.

## 5. Edge cases and constraints

- Index `0` is a valid index (only `null`/`undefined` mean "no index").
- The result does not depend on the current date, except when the weekday number is `NaN`
  (e.g. `('dddd')`, `('[On] dddd')`): then the name of today's (UTC) weekday is returned.
- Each call builds a new array; nothing is cached or mutated.

=== CONTEXT ===
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

=== STUB ===
```javascript
function listWeekdaysImpl (localeSorted, format, index, field) {
    // TODO: implement according to the specification
}
```
