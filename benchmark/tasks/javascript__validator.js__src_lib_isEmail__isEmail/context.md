# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/isEmail.js`

## Imports / includes available in this file

```
import assertString from './util/assertString';
import merge from './util/merge';
import isByteLength from './isByteLength';
import isFQDN from './isFQDN';
import isIP from './isIP';
```

## Other functions defined in the same file (signatures only; you may call them)

```
validateDisplayName ( display_name )
```

## Variables declared at the same scope level (you may use them)

```
const default_email_options = {
  allow_display_name: false,
  require_display_name: false,
  allow_utf8_local_part: true,
  require_tld: true,
};
const splitNameAddress = /^([^\x00-\x1F\x7F-\x9F\cX]+)<(.+)>$/i;
const emailUserPart = /^[a-z\d!#\$%&'\*\+\-\/=\?\^_`{\|}~]+$/i;
const gmailUserPart = /^[a-z\d]+$/;
const quotedEmailUser = /^([\s\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e]|(\\[\x01-\x09\x0b\x0c\x0d-\x7f]))*$/i;
const emailUserUtf8Part = /^[a-z\d!#\$%&'\*\+\-\/=\?\^_`{\|}~\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+$/i;
const quotedEmailUserUtf8 = /^([\s\x01-\x08\x0b\x0c\x0e-\x1f\x7f\x21\x23-\x5b\x5d-\x7e\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]|(\\[\x01-\x09\x0b\x0c\x0d-\x7f\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))*$/i;
const defaultMaxEmailLength = 254;
```

## Behaviour of the imported helpers and of the sibling function

- `assertString(input)` (default export of `./util/assertString`): returns nothing if `input` is a
  primitive string or a `String` object; otherwise throws a `TypeError` with the message
  `Expected string but received <type>.` (e.g. `a number`, `null`, `Array`).
- `merge(obj = {}, defaults)` (default export of `./util/merge`): for every key of `defaults`
  whose value in `obj` is `undefined`, copies the default into `obj`; returns `obj` (the same
  object, mutated; a new `{}` when `obj` is `undefined`). Keys already present with a
  non-`undefined` value (including `null`/`false`) are kept.
- `isByteLength(str, { min, max })` (default export of `./isByteLength`): `true` when the UTF-8
  byte length of `str` is at least `min` (default 0) and, if `max` is given, at most `max`.
- `isFQDN(str, options)` (default export of `./isFQDN`): `true` when `str` is a valid
  domain name. Options `require_tld` (default `true`: the last label must be a top-level
  domain of at least two letters and there must be at least two labels), `allow_underscores`
  (default `false`), `allow_trailing_dot` (default `false`). Labels may contain ASCII letters,
  digits, `-` and any character from U+00A1 upwards (except full-width forms), must be
  non-empty, at most 63 characters, and must not start or end with `-`.
- `isIP(str, version = '')` (default export of `./isIP`): `true` when `str` is an IPv4 address
  (`version` 4), an IPv6 address (`version` 6), or either (`version` omitted/empty). IPv4 is four
  dot-separated groups of 1-3 decimal digits each at most 255; IPv6 accepts `::` compression,
  an embedded IPv4 tail (`::ffff:1.2.3.4`) and a `%zone` suffix.
- `validateDisplayName(display_name)` (same file): returns `true` when `display_name` is an
  acceptable RFC 2822 display name. If the name is wrapped in double quotes (`"..."` with at
  least one character inside) only the inner text is examined. The (inner) text must not be
  empty or whitespace-only. If it contains any of `.` `"` `;` `<` `>`, the name must have been
  wrapped in double quotes and every `"` inside must be preceded by a backslash (`\"`);
  otherwise it returns `false`.
