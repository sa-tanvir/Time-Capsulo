You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
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

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/duration/valid.js`

## Imports / includes available in this file

```
import toInt from '../utils/to-int';
import indexOf from '../utils/index-of';
import {Duration} from './constructor';
import {createDuration} from './create';
```

## Other functions defined in the same file (signatures only; you may call them)

```
createInvalid ( )
isValid ( )
```

## Variables declared at the same scope level (you may use them)

```
var ordering = ['year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second', 'millisecond'];
```

## Behaviour of the imported helpers

- `toInt(x)`: converts `x` with unary `+` (number coercion); returns `0` when the result is `0`,
  `NaN` or `±Infinity`, otherwise the number truncated toward zero (`toInt('1.9') === 1`,
  `toInt(-2.5) === -2`, `toInt('1e3') === 1000`, `toInt(true) === 1`).
- `indexOf`: `Array.prototype.indexOf` (use as `indexOf.call(array, value)`).
- `ordering` (above): the nine canonical duration unit names, from the largest unit to the
  smallest.

=== STUB ===
```javascript
export default function isDurationValid(m) {
    // TODO: implement according to the specification
}
```
