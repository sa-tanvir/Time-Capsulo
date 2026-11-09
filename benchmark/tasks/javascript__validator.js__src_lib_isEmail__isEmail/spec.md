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
