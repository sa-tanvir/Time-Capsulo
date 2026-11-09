# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isIP.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous)
```

## Variables declared at the same scope level (you may use them)

```
const ipv4Maybe = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
const ipv6Block = /^[0-9A-F]{1,4}$/i;
```

## Behaviour of the imported helpers

- `assertString(input)` (default export of `./util/assertString`): returns nothing if `input` is a
  primitive string or a `String` object; otherwise throws a `TypeError` with the message
  `Expected string but received <type>.` (e.g. `a number`, `null`, `Array`).
