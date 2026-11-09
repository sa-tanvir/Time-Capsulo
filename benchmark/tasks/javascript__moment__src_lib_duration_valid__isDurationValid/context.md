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
