# Functional specification: `isDurationValid(m)` in `src/lib/duration/valid.js`

## 1. Component overview

Default export of the module. When a moment.js `Duration` is constructed, the user's input object
(e.g. `{days: 3, hours: 1.1}`) is first normalized so that every recognised alias becomes its
canonical unit name (`days`/`d` → `day`, `h` → `hour`, …). `isDurationValid` receives that
normalized object and decides whether the duration is valid; the result becomes
`duration.isValid()`. Invalid durations report `NaN` for all numeric getters.

## 2. Functional requirements

Return `false` if any of the following holds, otherwise `true`:

1. **Unknown key.** The object has an enumerable property (own or inherited, as visited by a
   `for…in` loop) whose name is not one of the nine canonical units in `ordering`:
   `year, quarter, month, week, day, hour, minute, second, millisecond`. Note that `isoWeek`,
   plural forms and abbreviations are *not* accepted here.
2. **Not a number.** A property's value is neither `null` nor `undefined` and the global
   `isNaN(value)` is true. So `NaN` and `'abc'` are rejected, while `null`, `undefined`, `''`,
   `true`, `'12'` and `Infinity` pass this rule.
3. **Fraction on a non-smallest unit.** Look at the units in `ordering` order (largest to smallest)
   and consider only units whose value is truthy (so `0`, `''`, `null`, `undefined`, `NaN` and
   `false` are skipped). A unit "has a fractional part" when `parseFloat(value)` differs
   (`!==`) from `toInt(value)` (see `context.md`). Once a considered unit has a fractional part,
   any *later* considered (smaller, truthy) unit makes the result `false`. In other words, only
   the smallest unit actually present may be non-integer.

Rule 3 uses `parseFloat` vs. `toInt`, so some values count as "fractional" although they look
integral: `'1e3'` (`1` vs `1000`), `Infinity`/`-Infinity` (`±Infinity` vs `0`), `true` (`NaN` vs
`1`). Negative decimals are fractional too (`-2.5`). Strings with surrounding spaces such as
`' 4 '` are integral (`4` vs `4`).

## 3. Input specification

- `m`: a plain object (the normalized duration input). Values are numbers, numeric strings,
  `null`/`undefined`, or arbitrary junk (`NaN`, booleans, other strings). The object may be empty.

## 4. Output specification

A boolean. Examples:

- `{}` → `true`; `{day: null}` → `true`
- `{day: 3.5, hour: 1.1}` → `false` (day is fractional and a smaller unit follows)
- `{day: 3, hour: 1.1}` → `true`
- `{year: 1.5, millisecond: 0}` → `true` (millisecond is 0, so not considered)
- `{year: 1.5, millisecond: 2}` → `false`
- `{hour: '1.5', second: '3'}` → `false`; `{month: '2'}` → `true`
- `{millisecond: NaN}` → `false`; `{month: 'abc'}` → `false`
- `{isoWeek: 2}` → `false`; `{days: 2}` → `false`; `{day: 1, foo: null}` → `false`
- `{day: Infinity}` → `true` (only one considered unit); `{day: -Infinity, hour: 1}` → `false`
- `{second: '1e3', millisecond: 5}` → `false`; `{day: true, hour: 2}` → `false`

## 5. Edge cases and constraints

- The object is not modified; no side effects.
- Rules 1–2 apply to every key regardless of its value; rule 3 only to the canonical units.
- The result does not depend on the order of the keys in the object.
