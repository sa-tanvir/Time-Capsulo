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
