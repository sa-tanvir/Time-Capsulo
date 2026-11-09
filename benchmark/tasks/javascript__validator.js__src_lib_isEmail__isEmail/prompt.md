You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `isEmail(str, options)` in `src/lib/isEmail.js`

## 1. Component overview

Public validator of the validator.js library (`validator.isEmail`). It decides whether a string
is an e-mail address, optionally with an RFC 2822 display name (`Some Name <foo@bar.com>`),
IP-literal domains, and Gmail-specific local-part rules. It returns a boolean.

## 2. Functional requirements

Perform the checks below in this order; the first failing check returns `false`.

1. **Type.** If `str` is not a string, throw the `TypeError` produced by `assertString`.
2. **Options.** Missing (`undefined`) option keys take the values of `default_email_options`
   (`allow_display_name: false`, `require_display_name: false`, `allow_utf8_local_part: true`,
   `require_tld: true`). Further options, all falsy by default: `ignore_max_length`,
   `allow_ip_domain`, `domain_specific_validation`. Options are tested for truthiness.
3. **Display name.** Only when `require_display_name` or `allow_display_name` is truthy:
   if the whole input matches `splitNameAddress` (see context), group 1 is the display name and
   group 2 becomes the address that all further steps examine. If the display name ends with a
   space, exactly one trailing space is dropped; then the name must be accepted by
   `validateDisplayName` (see context), else `false`. If the input does not match and
   `require_display_name` is truthy → `false`; if it does not match and only
   `allow_display_name` is set, the whole input is examined as a plain address.
4. **Total length.** Unless `ignore_max_length` is truthy, an address longer than 254 characters
   (UTF-16 length) → `false`.
5. **Split.** The domain is the text after the **last** `@`; the local part is everything before
   it (it may itself contain `@`). Without any `@`, the local part is empty and the domain is the
   whole address.
6. **Gmail rules.** Only when `domain_specific_validation` is truthy and the lower-cased domain is
   `gmail.com` or `googlemail.com`: lower-case the local part (`toLowerCase()`); this
   lower-cased local part **replaces** the original one for all later steps (7, 9 and 10). Take
   the part before the first `+`; that part with only its **first** `.` removed (later dots are
   kept and counted: `a.b.c` is measured as `ab.c`, 4 bytes) must have a UTF-8 byte length
   between 6 and 30 inclusive; and splitting that part (before `+`) on `.` must give only
   non-empty pieces of lowercase ASCII letters and digits (`gmailUserPart`). Otherwise `false`.
   The domain itself is never lower-cased for later steps.
7. **Byte lengths.** The local part must be at most 64 UTF-8 bytes and the domain at most 254
   UTF-8 bytes.
8. **Domain.** The domain must be accepted by `isFQDN`, called with an options object that
   carries only this function's `require_tld` setting (no other FQDN option is passed, so
   underscores and trailing dots are rejected). If it does
   not: when `allow_ip_domain` is falsy → `false`; otherwise the domain must be an IP address
   accepted by `isIP(domain)` (any version), or be `[` + a non-empty IP address + `]`
   (e.g. `[123.123.123.123]`, `[::1]`); otherwise `false`.
9. **Quoted local part.** If the local part starts with `"`, remove its first and last
   characters (whatever the last one is) and return whether the remainder fully matches
   `quotedEmailUserUtf8` when `allow_utf8_local_part` is truthy, else `quotedEmailUser`.
10. **Dot-atom local part.** Otherwise split the local part on `.`; every piece must be
    non-empty and fully match `emailUserUtf8Part` when `allow_utf8_local_part` is truthy, else
    `emailUserPart`. Return `true` if all pieces match.

## 3. Input specification

- `str`: any string. Non-strings throw `TypeError` (message `Expected string but received ...`).
- `options`: optional; `undefined` or a plain object with any of the options above. The
  function may fill defaults into the passed object (as `merge` does) but must not otherwise
  change it.

## 4. Output specification

A boolean. Examples (default options unless stated):

- valid: `'foo@bar.com'`, `'x@x.au'`, `'foo+bar@bar.com'`, `'hans.m端ller@test.com'`,
  `'hans@m端ller.com'`, `'test|123@m端ller.com'`, `'"foobar"@example.com'`,
  `'"  foo  m端ller "@example.com'`, `'"foo\\@bar"@example.com'` (JS literal), `'test.1@gmail.com'`,
  64 `a`s + `@` + 63 `a`s + `.com`
- invalid: `'invalidemail@'`, `'invalid.com'`, `'@invalid.com'`, `'foo@bar.com.'`, `'z@co.c'`,
  `'somename@ｇｍａｉｌ.com'`, `'test1@invalid.co m'`, `'multiple..dots@stillinvalid.com'`,
  `'ends.with.dot.@gmail.com'`, `'wrong()[]",:;<>@@gmail.com'`, 65 `a`s + `@b.com` style local
  parts over 64 bytes, 30 full-width `ｇｍａｉｌ` characters before `@gmail.com` (over 64 bytes),
  any address over 254 characters
- `{ domain_specific_validation: true }`: valid `'foobar@gmail.com'`, `'foo.bar@googlemail.com'`,
  30 `a`s + `@gmail.com`; invalid 31 `a`s + `@gmail.com`, `'test@gmail.com'`,
  `'test.1@gmail.com'`, `'.foobar@gmail.com'`
- `{ allow_utf8_local_part: false }`: `'hans.m端ller@test.com'` and `'tüst@invalid.com'` invalid,
  `'hans@m端ller.com'` and `'"  foo  bar  "@example.com'` valid
- `{ allow_display_name: true }`: valid `'Some Name <foo@bar.com>'`, `'Name<foo@bar.com>'`,
  `"'Foo Bar, Esq'<foo@bar.com>"`, `'"<displayNameInBrackets>"<jh@gmail.com>'`,
  `'"name;" <jh@gmail.com>'`, and plain `'foo@bar.com'`; invalid `'Some Name <invalid.com>'`,
  `'Some Name foo@bar.co.uk.>'`, `'Some Name < foo@bar.co.uk >'`, `'Name foo@bar.co.uk'`,
  `'invisibleCharacter\u001F<jh@gmail.com>'`, `'<displayNameInBrackets><jh@gmail.com>'`,
  `'name;<jh@gmail.com>'`, `'    <jh@gmail.com>'`, `'"    "<jh@gmail.com>'`
- `{ require_display_name: true }`: `'Some Name <foo@bar.com>'` valid, `'foo@bar.com'` invalid
- `{ allow_ip_domain: true }`: valid `'email@[123.123.123.123]'`, `'email@255.255.255.255'`;
  invalid `'email@0.0.0.256'`, `'email@[266.266.266.266]'`

## 5. Edge cases and constraints

- Byte lengths are UTF-8 lengths, so non-ASCII characters count 2-4 bytes each.
- `'"@example.com'` is valid (removing first and last character of `"` leaves an empty quoted
  string, which matches); `'a@b@c.com'` has local part `a@b`, which fails step 10.
- With `ignore_max_length` the 254-character limit is skipped but the byte limits of step 7
  still apply.
- Display names may be arbitrarily long; the address extracted from them is what steps 4-10
  check.
- Synchronous, no side effects other than the possible default-filling of `options`.

=== CONTEXT ===
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

=== STUB ===
```javascript
export default function isEmail(str, options) {
    // TODO: implement according to the specification
}
```
