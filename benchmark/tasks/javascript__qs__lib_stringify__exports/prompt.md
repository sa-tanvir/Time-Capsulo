You are an expert JavaScript developer.

Implement the function below so that it satisfies the functional specification.
The function will be inserted into an existing JavaScript code base in place of the original, so:
- keep the exact signature shown in the stub (name, parameters, defaults, return type);
- you may use the imports and call the other functions listed in the context; do not add anything outside the function
  (no module-level imports, helper functions or classes) - imports inside the function body are allowed;
- write efficient, production-quality code.

Return ONLY the complete function (signature and body) in a single ```javascript code block, with no explanation.

=== SPECIFICATION ===
# Functional specification: `module.exports = function (object, opts)` in `lib/stringify.js` (`qs.stringify`)

## 1. Component overview

The public entry point of the `qs` query-string serialiser. It turns a (possibly
nested) JavaScript object or array into a URL query string such as
`a=b&c%5B0%5D=d`. Option validation/normalisation is provided by
`normalizeStringifyOptions(opts)` and the per-key serialisation of a value
(including all nesting, filtering, date/null handling and encoding) by the
recursive helper `stringify(object, prefix, generateArrayPrefix, strictNullHandling,
skipNulls, encoder, filter, sort, allowDots, serializeDate, formatter,
encodeValuesOnly, charset)` (see `context.md`). That helper returns, for one
top-level key, either a string or an array of `key=value` strings; this function
orchestrates the call for every top-level key and assembles the final string.

## 2. Functional requirements

1. **Options.** Normalise `opts` with `normalizeStringifyOptions` (this is where
   invalid options throw, see §5). `opts` itself must never be mutated
   (`qs.stringify({}, o)` leaves `o` deep-equal to `{}`).
2. **Filter.** If the normalised `filter` is a function, it is first called once as
   `filter('', object)` and its return value replaces the input. If it is an array,
   that array is the list of top-level keys to emit (in that order) instead of the
   object's own keys; the array is also handed down to the helper, where it selects
   keys at every nesting level (including array indices).
3. **Non-object input.** If the (possibly filtered) input is not an object or is
   `null`, return `''` (e.g. `undefined`, `null`, `false`, `0`, `''`, a Symbol, a
   BigInt all give `''`). Arrays are objects: `qs.stringify([Symbol.iterator])` is
   `'0=Symbol%28Symbol.iterator%29'`, `qs.stringify([BigInt(3)])` is `'0=3'`.
4. **Array format.** Choose the array-prefix generator from the
   `arrayPrefixGenerators` table:
   - if `opts.arrayFormat` is one of its keys (`'indices'`, `'brackets'`,
     `'repeat'`, `'comma'`), use it;
   - else, if `opts` has an `indices` property (even `false`), use `'indices'` when
     it is truthy and `'repeat'` otherwise;
   - else `'indices'`.
   Results for `{ a: ['b','c','d'] }`: indices `a%5B0%5D=b&a%5B1%5D=c&a%5B2%5D=d`,
   brackets `a%5B%5D=b&a%5B%5D=c&a%5B%5D=d`, repeat / `indices:false`
   `a=b&a=c&a=d`, comma `a=b%2Cc%2Cd`.
5. **Keys.** Without an array filter, the top-level keys are the input's own
   enumerable keys (`Object.keys`; inherited properties such as ones added to
   `Object.prototype` are ignored; objects with a `null` prototype work). If a
   `sort` comparator was given, the top-level key list is sorted in place with it
   (when the key list is the filter array, that array itself gets sorted).
6. **Per key.** Skip the key when `skipNulls` is on and the value is exactly
   `null`. Otherwise call the helper with: the value, the key itself as prefix
   (top-level keys get no brackets), the chosen generator (function or the string
   `'comma'`), `strictNullHandling`, `skipNulls`, the encoder **or `null` when the
   `encode` option is `false`**, the normalised `filter`, `sort`, `allowDots`,
   `serializeDate`, `formatter`, `encodeValuesOnly`, `charset`. Append everything
   it returns (a single string or each element of an array) to the result list,
   preserving order.
7. **Assembly.** Join the collected pieces with `delimiter` (default `'&'`;
   `{ delimiter: ';' }` gives `a=b;c=d`). Build a prefix: `'?'` if
   `addQueryPrefix === true`; then, if `charsetSentinel` is on, append
   `'utf8=%26%2310003%3B&'` for charset `iso-8859-1`, otherwise
   `'utf8=%E2%9C%93&'`. Return prefix + joined string, **but return `''` when the
   joined string is empty** (so `qs.stringify({}, { addQueryPrefix: true })` is `''`).

## 3. Input specification

- `object`: any value; normally a plain object or array, possibly nested, whose
  leaves may be strings, numbers, booleans, Symbols, BigInts, `null`, `undefined`,
  `Date`s or Buffers.
- `opts` (optional object). Recognised options and defaults:
  `addQueryPrefix` (false), `allowDots` (false; nested keys as `a.b` instead of
  `a[b]`), `arrayFormat`, `indices` (see 4), `charset` (`'utf-8'` or
  `'iso-8859-1'`), `charsetSentinel` (false), `delimiter` (`'&'`), `encode`
  (true), `encoder` (function `(value, defaultEncoder, charset, type)` with
  `type` `'key'` or `'value'`; default `utils.encode`, which is also the
  `defaultEncoder` argument), `encodeValuesOnly` (false), `filter` (function
  `(prefix, value)` or array of keys), `format` (`'RFC3986'` default or
  `'RFC1738'`), `serializeDate` (function `(date)`; default is
  `Date.prototype.toISOString` called on the date, even if the instance shadows
  `toISOString`), `skipNulls` (false), `sort` (comparator or null),
  `strictNullHandling` (false).

## 4. Output specification

A string. Examples:

- `{ a: 'b' }` -> `a=b`; `{ a: 1, b: 2 }` -> `a=1&b=2`; `{ a: '€' }` -> `a=%E2%82%AC`;
  `{ a: 'b c' }` -> `a=b%20c`; with `format:'RFC1738'` -> `a=b+c`, and
  `{ 'a b': 'c d' }` -> `a+b=c+d`.
- `{ a: { b: { c: { d: 'e' } } } }` -> `a%5Bb%5D%5Bc%5D%5Bd%5D=e`; with `allowDots` -> `a.b.c.d=e`.
- `{ a: [{ b: 1 }, 2, 3] }`, `encode:false`, brackets -> `a[][b]=1&a[]=2&a[]=3`;
  `{ a: [{ b: 'c' }] }`, `indices:false` -> `a%5Bb%5D=c`.
- `{ a: null, b: '' }`, `strictNullHandling` -> `a&b=`; without it `{ a: null }` -> `a=`.
- `{ a: undefined }` -> `''`; `{ a: { b: undefined, c: '' } }` -> `a%5Bc%5D=`.
- `{ a: 'b', c: ['d', 'e=f'], f: [['g'], ['h']] }`, `encodeValuesOnly` ->
  `a=b&c[0]=d&c[1]=e%3Df&f[0][0]=g&f[1][0]=h`.
- `{ æ: 'æ' }`, charset `iso-8859-1` -> `%E6=%E6`; `{ a: '☺' }` -> `a=%26%239786%3B`.
- `{ a: 'æ' }`, `charsetSentinel`, utf-8 -> `utf8=%E2%9C%93&a=%C3%A6`; iso-8859-1 ->
  `utf8=%26%2310003%3B&a=%E6`.
- sort with `localeCompare`: `{ a:'c', z:{ j:'a', i:'b' }, b:'f' }` -> `a=c&b=f&z%5Bi%5D=b&z%5Bj%5D=a`.
- filter `['a','b',0,2]` on `{ a: { b: [1,2,3,4], c: 'd' }, c: 'f' }` ->
  `a%5Bb%5D%5B0%5D=1&a%5Bb%5D%5B2%5D=3`; filter `[]` -> `''`.
- A function filter returning `undefined` for prefix `c` and `date.getTime()` for a
  Date at `e[f]` turns `{ a:'b', c:'d', e:{ f: date } }` into `a=b&e%5Bf%5D=1257894000000`
  (5 calls in total: once with `''` and the whole object, then per nested value).
- Custom encoder lower-casing keys and upper-casing values: `{ KeY: 'vAlUe' }` -> `key=VALUE`.
- Buffers are leaves: `{ a: Buffer.from('test') }` -> `a=test`; a custom encoder
  receives the Buffer object itself.

## 5. Edge cases and constraints

- Invalid options throw `TypeError` (from option normalisation):
  `encoder` neither a function nor null/undefined -> `'Encoder has to be a function.'`;
  `charset` defined but not `'utf-8'`/`'iso-8859-1'` ->
  `'The charset option must be either utf-8, iso-8859-1, or undefined'`;
  `format` defined but not a known formatter name (e.g. `'UFO1234'`, `false`,
  `1234`, `null`, `{}`, `[]`) -> `'Unknown format option provided.'`.
- `encode: false` disables encoding entirely (`{ a: { b: 'c' } }` -> `a[b]=c`), but
  the formatter is still applied.
- A custom encoder is called once for the key and once for the value of each leaf
  (`qs.stringify({ a: 1 }, { encoder })` calls it exactly twice), receiving
  `utils.encode` as second argument.
- `serializeDate` returning `null` with `strictNullHandling` gives just the key
  (`key`). A function filter that returns the value unchanged keeps
  `strictNullHandling` behaviour (`{ key: null }` -> `key`).
- Must work when the global `Buffer` is absent.
- Pure apart from the documented in-place sort of a filter array; the input object
  is not modified.

=== CONTEXT ===
# Context for the function to implement

- **Language:** javascript
- **File:** `lib/stringify.js`

## Imports / includes available in this file

```
var utils = require('./utils');
var formats = require('./formats');
```

## Other functions defined in the same file (signatures only; you may call them)

```
brackets ( prefix )
indices ( prefix , key )
isNonNullishPrimitive ( v )
normalizeStringifyOptions ( opts )
pushToArray ( arr , valueOrArray )
repeat ( prefix )
serializeDate ( date )
stringify ( object , prefix , generateArrayPrefix , strictNullHandling , skipNulls , encoder , filter , sort , allowDots , serializeDate , formatter , encodeValuesOnly , charset )
```

## Variables declared at the same scope level (you may use them)

```
var has = Object.prototype.hasOwnProperty;
var arrayPrefixGenerators = {
    brackets: function brackets(prefix) {
        return prefix + '[]';
    },
    comma: 'comma',
    indices: function indices(prefix, key) {
        return prefix + '[' + key + ']';
    },
    repeat: function repeat(prefix) {
        return prefix;
    }
};
var isArray = Array.isArray;
var push = Array.prototype.push;
var toISO = Date.prototype.toISOString;
var defaultFormat = formats['default'];
var defaults = {
    addQueryPrefix: false,
    allowDots: false,
    charset: 'utf-8',
    charsetSentinel: false,
    delimiter: '&',
    encode: true,
    encoder: utils.encode,
    encodeValuesOnly: false,
    format: defaultFormat,
    formatter: formats.formatters[defaultFormat],
    // deprecated
    indices: false,
    serializeDate: function serializeDate(date) {
        return toISO.call(date);
    },
    skipNulls: false,
    strictNullHandling: false
};
```

## Helper contracts (same file)

- `normalizeStringifyOptions(opts)`: validates and normalises the options.
  - If `opts` is falsy, it returns the module-level `defaults` object itself (shown above;
    it has no `filter` and no `sort` property, so both read as `undefined`).
  - Otherwise it throws the `TypeError`s listed in the spec (checked in this order: encoder,
    charset, format) and returns a **new** object with exactly these fields:
    `addQueryPrefix` (boolean, default `false`), `allowDots` (`!!opts.allowDots`, default
    `false`), `charset` (`opts.charset || 'utf-8'`), `charsetSentinel` (boolean, default
    `false`), `delimiter` (`opts.delimiter` if defined, else `'&'`), `encode` (boolean, default
    `true`), `encoder` (`opts.encoder` if a function, else `utils.encode`), `encodeValuesOnly`
    (boolean, default `false`), `filter` (`opts.filter` if it is a function or an array, else
    `undefined`), `formatter` (the formatter function for `opts.format`, default RFC3986, i.e.
    `String(v)`; RFC1738 replaces every `%20` with `+`), `serializeDate` (`opts.serializeDate`
    if a function, else the default ISO serialiser), `skipNulls` (boolean, default `false`),
    `sort` (`opts.sort` if a function, else `null`), `strictNullHandling` (boolean, default
    `false`). Boolean fields take the option only when it is of type boolean, otherwise the
    default. The returned object has no `arrayFormat`, `indices` or `format` field: the array
    format must be read from the raw `opts`.
- `pushToArray(arr, valueOrArray)`: appends every element of `valueOrArray` to `arr` when it is
  an array, otherwise appends `valueOrArray` itself; mutates `arr`, returns `undefined`.

=== STUB ===
```javascript
module.exports = function (object, opts) {
    // TODO: implement according to the specification
}
```
