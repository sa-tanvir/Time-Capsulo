# Functional specification: private helper `stringify` (13 positional parameters, see `stub.js`) in `lib/stringify.js`

## 1. Component overview

Private recursive helper of the `qs` query-string serialiser. It serialises one
value that lives under a given (already built, not yet encoded) key path
`prefix` into the list of `key=value` pieces for that value and everything nested
inside it. The public `qs.stringify(obj, opts)` (`module.exports`) normalises the
options, then for each top-level key `k` of `obj` (skipping `null` values when
`skipNulls` is on) calls this helper with `object = obj[k]` and `prefix = k`
(top-level keys get no brackets), appends whatever it returns (a single string or
every element of an array) to one list, and joins that list with the delimiter
(default `&`). So `qs.stringify({ a: { b: 'c' } })` is `'a%5Bb%5D=c'` because the
helper returns `['a%5Bb%5D=c']` for object `{ b: 'c' }` with prefix `'a'`.

## 2. Functional requirements

Given the value `object` at path `prefix`:

1. **Pre-processing (exactly one of these, in priority order):**
   - if `filter` is a function, call `filter(prefix, object)` and continue with its
     return value instead (no date serialisation or comma joining is then applied);
   - else if the value is a `Date`, continue with `serializeDate(date)`;
   - else if `generateArrayPrefix` is the string `'comma'` and the value is an
     array, continue with the elements joined by `','` (standard array join, so an
     empty array becomes `''`).
2. **null:** if the value is now `null`:
   - with `strictNullHandling`, return just the key, with no `=`: the key passed
     through `encoder(prefix, defaultEncoder, charset, 'key')` when an encoder is
     given and `encodeValuesOnly` is false, otherwise the raw `prefix`. The
     formatter is not applied here. The result may be returned as a bare string.
   - otherwise treat it as the empty string `''`.
3. **Leaves:** primitive strings, numbers, booleans, Symbols and BigInts (exactly the
   values for which `isNonNullishPrimitive` is true; boxed primitives such as
   `new String('ab')` are containers, see rule 5) and Buffers (as recognised by
   `utils.isBuffer`) produce a one-element array `[K + '=' + V]`:
   - with an encoder: `K = formatter(encodeValuesOnly ? prefix :
     encoder(prefix, defaultEncoder, charset, 'key'))` and
     `V = formatter(encoder(value, defaultEncoder, charset, 'value'))`. The key is
     encoded before the value; the value is passed to the encoder unconverted
     (a Buffer, number, Symbol, ... is handed over as is).
   - without an encoder (`null`): `K = formatter(prefix)`,
     `V = formatter(String(value))`.
   `defaultEncoder` is always the library default `utils.encode` (`defaults.encoder`).
4. **undefined:** return an empty array (nothing emitted).
5. **Containers** (objects, arrays, anything else): determine the child keys:
   if `filter` is an array, exactly its entries in its order (missing children
   are `undefined` and emit nothing); otherwise the value's own enumerable keys
   (`Object.keys`), sorted with `sort` when a comparator is given. For each key,
   skip it when `skipNulls` is on and the child is exactly `null`; otherwise
   recurse with the same settings and child path:
   - parent is an array: `generateArrayPrefix(prefix, key)` when it is a function
     (`indices` -> `p[0]`, `brackets` -> `p[]`, `repeat` -> `p`), else `prefix`
     unchanged;
   - otherwise: `prefix + '.' + key` when `allowDots`, else `prefix + '[' + key + ']'`.
   Concatenate all children's results in key order and return the array (possibly
   empty, e.g. for `{}`, `[]`, or a Date when a function filter left it unchanged).

## 3. Input specification

- `object`: any value.
- `prefix`: string key path built so far (raw, unencoded), e.g. `'a[b][0]'`, `'a.b'`.
- `generateArrayPrefix`: one of the functions in `arrayPrefixGenerators`, or the
  string `'comma'`.
- `strictNullHandling`, `skipNulls`, `allowDots`, `encodeValuesOnly`: booleans.
- `encoder`: `null`/falsy (encoding disabled, public `encode:false`) or a function
  `(value, defaultEncoder, charset, type)` with `type` `'key'` or `'value'`,
  returning a string.
- `filter`: `undefined`, a function `(prefix, value) -> newValue`, or an array of keys
  (strings/numbers) applied at every level.
- `sort`: comparator `(a, b)` or `null`.
- `serializeDate`: function `(date) -> value` (default: ISO string).
- `formatter`: function applied to each encoded key and value string (RFC3986:
  `String(v)`; RFC1738: replaces every `%20` with `+`).
- `charset`: `'utf-8'` or `'iso-8859-1'`, only forwarded to the encoder.

## 4. Output specification

An array of `key=value` strings in emission order, or (only in the
`strictNullHandling` null case) a bare key string. Examples via the public API
(default encoder, RFC3986):

- `{ a: { b: { c: null } } }` -> `a%5Bb%5D%5Bc%5D=`; with `strictNullHandling` -> `a%5Bb%5D%5Bc%5D`.
- `{ a: [{ b: { c: [1] } }] }`, `encode:false`, dots + indices -> `a[0].b.c[0]=1`; brackets -> `a[].b.c[]=1`.
- `{ a: { b: ['c','d'] } }`, comma -> `a%5Bb%5D=c%2Cd`; with `encode:false, allowDots` -> `a.b=c,d`.
- `{ a: ['b','c'] }`, repeat -> `a=b&a=c`.
- `{ a: { b: 'c', d: null } }`, `skipNulls` -> `a%5Bb%5D=c`.
- filter `['a','b',0,2]` on `{ a: { b: [1,2,3,4], c: 'd' }, c: 'f' }` -> `a%5Bb%5D%5B0%5D=1&a%5Bb%5D%5B2%5D=3`.
- `{ a: 'b', c: ['d','e=f'], f: [['g'],['h']] }`, `encodeValuesOnly` -> `a=b&c[0]=d&c[1]=e%3Df&f[0][0]=g&f[1][0]=h`.
- `{ a: { b: null } }`, `encodeValuesOnly` + `strictNullHandling` -> `a[b]`.
- `{ a: true }` -> `a=true`; `{ a: Buffer.from('test') }` -> `a=test`;
  `{ 'a b': Buffer.from('a b') }` with RFC1738 -> `a+b=a+b`.
- `{ a: Symbol.iterator }` -> `a=Symbol%28Symbol.iterator%29`; `{ a: BigInt(3) }` -> `a=3`.
- `{ a: date }` -> `a=` + encoded ISO string; `serializeDate: d => d.getTime() * 7`
  on `new Date(6)` -> `a=42`; `serializeDate` returning `null` + `strictNullHandling` -> `key`.
- Encoder lower-casing `'key'` and upper-casing `'value'` results: `{ KeY: 'vAlUe' }` -> `key=VALUE`.
- A custom encoder on `{ a: Buffer.from([1]) }` receives the Buffer itself as value.

## 5. Edge cases and constraints

- The function filter is called for every visited value (including leaves and
  `undefined`/`null` children that are not skipped), with the child's path as
  `prefix`; returning `undefined` drops that entry.
- `skipNulls` checks the raw child value before any filter/serialisation.
- Inherited (prototype) properties are never emitted; null-prototype objects work.
- Must not rely on a global `Buffer`; must not mutate `object`, `filter` or other
  arguments.
- No depth limit; no cycle detection is required.
