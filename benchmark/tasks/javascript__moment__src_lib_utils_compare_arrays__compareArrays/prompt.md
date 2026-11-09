You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `compareArrays(array1, array2, dontConvert)` in `src/lib/utils/compare-arrays.js`

## 1. Component overview

Small utility (the module's default export) of moment.js that counts how many positions differ
between two arrays. moment uses it in two places:

- locale selection (`moment.locale(['en-au', 'en-gb'])`): locale names are split on `-` and the
  parts are compared as plain values (`dontConvert = true`) to decide whether the next candidate
  name is a more specific variant of the current root;
- `isDSTShifted()`: the date parts the user parsed (`[year, month, day, hour, …]`) are compared
  with the parts of the resulting moment after converting both sides to integers.

## 2. Functional requirements

1. Walk the positions that exist in **both** arrays (indices `0 … min(len1, len2) - 1`).
2. A position counts as a difference when:
   - `dontConvert` is truthy: the two elements are not strictly equal (`!==`, no coercion);
   - `dontConvert` is falsy (including `undefined`/omitted): the integer values of the two
     elements, as produced by the imported `toInt` helper (see `context.md`), are different.
     So `'1'` and `1` are equal, `'1.9'` and `1` are equal, and every non-numeric string, `null`,
     `undefined` or `NaN` counts as `0`.
3. Every element that one array has beyond the length of the other counts as one additional
   difference, regardless of its value.
4. Return the total: number of differing common positions plus the absolute length difference.

## 3. Input specification

- `array1`, `array2`: array-like values with a numeric `length` and indexed elements (in moment:
  arrays of numbers, numeric strings or lower-case strings). Either may be empty.
- `dontConvert`: optional; any value, only its truthiness matters.

## 4. Output specification

A non-negative integer (`number`). Examples:

- `compareArrays(['en', 'au'], ['en', 'gb'], true)` → `1`
- `compareArrays(['en'], ['en', 'gb'], true)` → `1` (only the length difference)
- `compareArrays(['en', 'gb'], ['en'], true)` → `1`
- `compareArrays(['zh', 'tw'], ['zh', 'tw'], true)` → `0`
- `compareArrays([], [1, 2, 3])` → `3`
- `compareArrays([2010, 1, 14], [2010, 1, 15, 0])` → `2`
- `compareArrays(['1', '2'], [1, 2])` → `0`, but `compareArrays(['1', '2'], [1, 2], true)` → `2`
- `compareArrays(['1.9', -2.7], [1, -2])` → `0`
- `compareArrays(['abc', null], [0, 0])` → `0`

In locale selection the result is checked against thresholds such as "at least `j - 1` parts
differ", e.g. `['en', 'au']` vs `['en', 'gb']` gives 1, so when trying the first `j = 2` parts of
`en-au` the next name `en-gb` is considered a sibling variant.

## 5. Edge cases and constraints

- Two empty arrays → `0`.
- With `dontConvert` truthy, `null` vs `null` is equal, `'1'` vs `1` differs, `-0` vs `0` is
  equal (strict equality).
- Without `dontConvert`, values whose number coercion is `NaN`, `Infinity` or `-Infinity` count
  as `0` (`'Infinity'` vs `0` is equal), while large finite numbers keep their truncated value
  (`1e300` vs `0` differs).
- Pure function: the arrays are not modified, no side effects, no dependency on time zone or locale.
- Must be efficient for long arrays (linear in the array lengths).

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/utils/compare-arrays.js`

## Imports / includes available in this file

```
import toInt from './to-int';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(none)
```

## Behaviour of the imported helpers

- `toInt(x)`: converts `x` with unary `+` (number coercion); returns `0` when the result is `0`,
  `NaN` or `±Infinity`, otherwise the number truncated toward zero (`toInt('1.9') === 1`,
  `toInt(-2.7) === -2`, `toInt('abc') === 0`, `toInt(null) === 0`, never `-0`).

=== STUB ===
```javascript
export default function compareArrays(array1, array2, dontConvert) {
    // TODO: implement according to the specification
}
```
