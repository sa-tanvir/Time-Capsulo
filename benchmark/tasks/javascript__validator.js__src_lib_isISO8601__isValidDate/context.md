# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isISO8601.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
```

## Other functions defined in the same file (signatures only; you may call them)

```
isISO8601 ( str , options )
```

## Variables declared at the same scope level (you may use them)

```
const iso8601 = /^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-3])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$/;
```
