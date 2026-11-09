# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isURL.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import isFQDN from './isFQDN';
import isIP from './isIP';
import merge from './util/merge';
```

## Other functions defined in the same file (signatures only; you may call them)

```
isRegExp ( obj )
isURL ( url , options )
```

## Variables declared at the same scope level (you may use them)

```
const default_url_options = {
  protocols: ['http', 'https', 'ftp'],
  require_tld: true,
  require_protocol: false,
  require_host: true,
  require_valid_protocol: true,
  allow_underscores: false,
  allow_trailing_dot: false,
  allow_protocol_relative_urls: false,
};
const wrapped_ipv6 = /^\[([^\]]+)\](?::([0-9]+))?$/;
```

## Behaviour of the sibling helper

- `isRegExp(obj)` (same file): returns `true` when `Object.prototype.toString.call(obj)` is
  `'[object RegExp]'`, i.e. `obj` is a regular expression object; `false` otherwise.
