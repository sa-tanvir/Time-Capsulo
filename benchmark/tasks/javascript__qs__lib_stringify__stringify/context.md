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
module.exports ( object , opts )
normalizeStringifyOptions ( opts )
pushToArray ( arr , valueOrArray )
repeat ( prefix )
serializeDate ( date )
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

- `isNonNullishPrimitive(v)`: `true` exactly when `typeof v` is `'string'`, `'number'`,
  `'boolean'`, `'symbol'` or `'bigint'`; `false` for everything else (`null`, `undefined`,
  objects, arrays, functions, boxed primitives such as `new String('a')`).
- `pushToArray(arr, valueOrArray)`: appends every element of `valueOrArray` to `arr` when it is
  an array, otherwise appends `valueOrArray` itself; mutates `arr`, returns `undefined`.
- `utils.isBuffer(obj)`: `true` when `obj` is a non-null object whose `constructor.isBuffer`
  exists and returns truthy for `obj` (Node `Buffer`s); `false` otherwise, including when no
  global `Buffer` exists.
