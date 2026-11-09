# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isIn.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import toString from './util/toString';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(none)
```

## Behaviour of the imported helpers

- `assertString(input)` (default export of `./util/assertString`): returns nothing if `input` is a
  primitive string or a `String` object; otherwise throws a `TypeError` with the message
  `Expected string but received <type>.` (e.g. `a number`, `null`, `Array`).
- `toString(input)` (default export of `./util/toString`): converts any value to a string:
  objects with a callable `toString` method use it, other objects give `'[object Object]'`,
  `null`/`undefined`, `NaN` and values for which `isNaN` is true and that have no non-zero
  `length` (e.g. functions with no parameters) give `''`, everything else gives `String(input)`.
