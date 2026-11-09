You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `isIP(str, version = '')` in `src/lib/isIP.js`

## 1. Component overview

Public validator of the validator.js library (`validator.isIP`). It checks whether a string is
an IP address: IPv4 (`'127.0.0.1'`), IPv6 (`'2001:db8::1'`, `'::ffff:127.0.0.1'`,
`'fe80::1234%eth0'`), or either. `isEmail`, `isURL` and `isIPRange` rely on it.

## 2. Functional requirements

1. If `str` is not a string, throw the `TypeError` produced by `assertString` (see context).
   This happens before the version is looked at.
2. `version` is converted with `String(version)`:
   - `''` (the default, also when `undefined` is passed): return `true` if `str` is a valid
     IPv4 address **or** a valid IPv6 address;
   - `'4'` (e.g. `4`, `'4'`, `4.0`): IPv4 rules only;
   - `'6'`: IPv6 rules only;
   - anything else (`10`, `0`, `null` → `'null'`, ...): return `false`.
3. **IPv4**: the whole string must be exactly four groups of 1 to 3 ASCII digits separated by
   single dots, nothing before or after, and each group's numeric value must be ≤ 255. Leading
   zeros are allowed as long as a group has at most 3 digits (`'01.02.03.004'` is valid,
   `'0200.200.200.200'` is not).
4. **IPv6**:
   1. Zone suffix: if the string contains `%`, it must contain exactly one `%`; the part before
      it (the address) must contain at least one `:`; the part after it (the zone) must be
      non-empty and may contain anything. Otherwise `false`. Without `%` the whole string is the
      address.
   2. Split the address on `:` into fields (`'::1'` gives the three fields `''`, `''`, `'1'`).
      If the last field is a valid IPv4 address (rule 3), it is an *IPv4 tail* and the field
      limit is 7, otherwise 8. More fields than the limit → `false` (this count includes the
      empty fields produced by `::`, e.g. `'::1:2:3:4:5:6:7'` and `'1:2:3:4:5:6:7::'` have 9
      fields and are invalid).
   3. The input exactly equal to `'::'` is valid.
   4. If the **input** starts with `::`, the two leading empty fields are discarded and the
      address counts as compressed. Otherwise, if the **input** (including any zone suffix)
      ends with `::`, the two trailing empty fields are discarded and the address counts as
      compressed. (So for `'fe80::%1'` no trailing compression is recognised, its last field
      is empty, and the result is `false`.)
   5. Check the remaining fields in order: an empty field that is neither the first nor the
      last remaining field marks a `::` inside the address; it is allowed only if the address
      is not already compressed (otherwise `false`, e.g. `'::1::'`, `'1::2::3'`), and it makes
      the address compressed. The last field may be the IPv4 tail. Every other field must be 1
      to 4 hexadecimal digits (any case); anything else (including an empty first/last field,
      as in `':1'` or `'1:'`) gives `false`.
   6. If the address is compressed the result is `true`; otherwise it is `true` only if there
      are exactly 8 fields (7 with an IPv4 tail).

## 3. Input specification

- `str`: any string (possibly empty or very long). Non-strings throw `TypeError`.
- `version`: optional; usually `4`, `6`, `'4'`, `'6'` or omitted, but any value is accepted and
  converted with `String`.

## 4. Output specification

A boolean. Examples (`version` omitted unless stated):

- valid: `'127.0.0.1'`, `'0.0.0.0'`, `'255.255.255.255'`, `'::1'`, `'2001:db8:0000:1:1:1:1:1'`,
  `'2001:41d0:2:a141::1'`, `'::ffff:127.0.0.1'`, `'::0000'`, `'0000::'`, `'1::'`, `'::'`,
  `'1111:1:1:1:1:1:1:1'`, `'fe80::a6db:30ff:fe98:e946'`, `'0:0:0:0:0:ffff:127.0.0.1'`,
  `'1:2:3::4:5:6:7'`, `'1::1.2.3.4'`
- invalid: `'abc'`, `'256.0.0.0'`, `'0.0.0.256'`, `'0200.200.200.200'`, `'::banana'`,
  `'banana::'`, `'::1banana'`, `'::1::'`, `'1:'`, `':1'`, `':1:1:1::2'`, `'::11111'`,
  `'11111:1:1:1:1:1:1:1'`, `'2001:db8:0000:1:1:1:1::1'`, `'0:0:0:0:0:0:ffff:127.0.0.1'`,
  `'0:0:0:0:ffff:127.0.0.1'`, `'1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1'`
- `isIP('127.0.0.1', 4)` → `true`; `isIP('::1', 4)` → `false`; `isIP('127.0.0.1', 6)` → `false`
- `isIP(x, 6)` valid: `'fe80::1234%1'`, `'ff08::9abc%interface10'`, `'ff02::5678%pvc1.3'`;
  invalid: `'::ffff:287.0.0.1'`, `'%'`, `'fe80::1234%'`, `'fe80::1234%1%3%4'`, `'fe80%fe80%'`
- `isIP('127.0.0.1', 10)` → `false`; `isIP('::1', 0)` → `false`

## 5. Edge cases and constraints

- Zones are only accepted in IPv6 mode; `'1.2.3.4%1'` is invalid in every mode.
- Whitespace anywhere makes the string invalid; non-ASCII digits are not digits.
- No length limit: very long strings (long zones, many fields) are simply evaluated by the
  rules above (e.g. a 2,000-character zone after a valid address is valid).
- Pure function: no mutation, no side effects.

=== CONTEXT ===
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

=== STUB ===
```javascript
export default function isIP(str, version = '') {
    // TODO: implement according to the specification
}
```
