You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `pickBy(fn, moments)` in `src/lib/moment/min-max.js`

## 1. Component overview

Module-private helper of moment.js behind `moment.min(...)` and `moment.max(...)`. It picks one
element out of a list of moment objects using a pairwise comparison method named by `fn`:
`'isBefore'` selects the earliest moment (min), `'isAfter'` the latest (max). Invalid moments
"win": as soon as the list contains an invalid moment, an invalid moment is returned.

## 2. Functional requirements

1. **Argument forms.** `moments` is the list of arguments the public function received. If it
   has exactly one element and that element is an array, that inner array is the list to use
   (`moment.min([a, b, c])` behaves like `moment.min(a, b, c)`).
2. **Empty list.** If the (possibly unwrapped) list is empty, return a new moment for the current
   time, created with the imported `createLocal()` with no arguments.
3. **Selection.** Start with the first element as the current pick and go through the remaining
   elements in order. An element replaces the current pick when it is invalid
   (`isValid()` returns false), or when calling its method `fn` with the current pick as argument
   returns true (e.g. `element.isBefore(pick)`). Consequences:
   - only strictly earlier (min) / later (max) moments replace the pick, so among equal instants
     the **first** one in the list is returned;
   - if the list contains invalid moments after the first position, the **last** invalid one is
     returned (valid moments never compare true against an invalid pick);
   - if only the first element is invalid, it stays the pick and is returned.
4. Return the selected element itself (the same object, not a copy).

## 3. Input specification

- `fn`: the name of a comparison method present on moment objects; in practice `'isBefore'` or
  `'isAfter'` (see `context.md`).
- `moments`: an array of moment objects, or an array whose single element is an array of moment
  objects. Moments may be valid or invalid; they may be in UTC or local mode.

## 4. Output specification

One of the input moment objects (identity preserved), or a fresh "now" moment for an empty list.
Examples with `past < now < future` (valid) and `invalid = moment.invalid()`:

- `pickBy('isBefore', [now, future, past])` → `past`
- `pickBy('isBefore', [[now, future, past]])` → `past`
- `pickBy('isAfter', [past, future, now])` → `future`
- `pickBy('isAfter', [now, past])` → `now`
- `pickBy('isBefore', [now])` → `now`; `pickBy('isAfter', [[now]])` → `now`
- `pickBy('isBefore', [[now, invalid]])` → `invalid`; `pickBy('isBefore', [[invalid, now]])` → `invalid`
- `pickBy('isAfter', [invalid, now])` → `invalid`
- `pickBy('isBefore', [a, b])` with `a` and `b` at the same instant → `a`

## 5. Edge cases and constraints

- Neither the list nor the moments are modified.
- Lists may be long (thousands of moments); a single pass over the list is expected.
- No dependency on the host time zone except through the moments themselves; only the empty-list
  case depends on the current time.

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/moment/min-max.js`

## Imports / includes available in this file

```
import { deprecate } from '../utils/deprecate';
import isArray from '../utils/is-array';
import { createLocal } from '../create/local';
import { createInvalid } from '../create/valid';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( )
max ( )
min ( )
```

## Behaviour of the imported helpers and of the moment methods involved

- `isArray(x)`: `true` when `x` is an array.
- `createLocal()` (no arguments): a new valid moment for the current time in local mode
  (what `moment()` returns).
- A moment object `m` has `m.isValid()` (boolean) and the comparison methods
  `m.isBefore(other)` / `m.isAfter(other)`: `true` when both moments are valid and `m`'s instant is
  strictly earlier / strictly later than `other`'s; `false` otherwise (equal instants, or either
  moment invalid).
- Callers: `min()` (exported) calls `pickBy('isBefore', [...arguments])`, `max()` calls
  `pickBy('isAfter', [...arguments])`; they back `moment.min(...)` / `moment.max(...)`.

=== STUB ===
```javascript
function pickBy(fn, moments) {
    // TODO: implement according to the specification
}
```
