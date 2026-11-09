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
