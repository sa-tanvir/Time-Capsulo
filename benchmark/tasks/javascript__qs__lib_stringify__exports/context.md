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
