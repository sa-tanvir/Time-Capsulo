# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isFQDN.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import merge from './util/merge';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(none)
```

## Variables declared at the same scope level (you may use them)

```
const default_fqdn_options = {
  require_tld: true,
  allow_underscores: false,
  allow_trailing_dot: false,
};
```

## Behaviour of the imported helpers

- `assertString(input)` (default export of `./util/assertString`): returns nothing if `input` is a
  primitive string or a `String` object; otherwise throws a `TypeError` with the message
  `Expected string but received <type>.` (e.g. `a number`, `null`, `Array`).
- `merge(obj = {}, defaults)` (default export of `./util/merge`): for every key of `defaults`
  whose value in `obj` is `undefined`, copies the default into `obj`; returns `obj` (the same
  object, mutated; a new `{}` when `obj` is `undefined`). Keys already present with a
  non-`undefined` value (including `null`/`false`) are kept.
