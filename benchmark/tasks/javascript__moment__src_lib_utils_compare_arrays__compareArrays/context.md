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
