```javascript
var stringify = function stringify(
    object,
    prefix,
    generateArrayPrefix,
    strictNullHandling,
    skipNulls,
    encoder,
    filter,
    sort,
    allowDots,
    serializeDate,
    formatter,
    encodeValuesOnly,
    charset
) {
    var obj = object;
    if (typeof filter === 'function') {
        obj = filter(prefix, obj);
    } else if (obj instanceof Date) {
        obj = serializeDate(obj);
    } else if (generateArrayPrefix === 'comma' && isArray(obj)) {
        obj = obj.join(',');
    }

    if (obj === null) {
        if (strictNullHandling) {
            return encoder && !encodeValuesOnly
                ? encoder(prefix, defaults.encoder, charset, 'key')
                : prefix;
        }

        obj = '';
    }

    if (isNonNullishPrimitive(obj) || utils.isBuffer(obj)) {
        if (encoder) {
            var keyValue = encodeValuesOnly
                ? prefix
                : encoder(prefix, defaults.encoder, charset, 'key');
            return [
                formatter(keyValue) + '='
                + formatter(encoder(obj, defaults.encoder, charset, 'value'))
            ];
        }
        return [formatter(prefix) + '=' + formatter(String(obj))];
    }

    var values = [];

    if (typeof obj === 'undefined') {
        return values;
    }

    var objKeys;
    if (isArray(filter)) {
        objKeys = filter;
    } else {
        objKeys = Object.keys(obj);
        if (sort) {
            objKeys.sort(sort);
        }
    }

    var objIsArray = isArray(obj);

    for (var i = 0; i < objKeys.length; ++i) {
        var key = objKeys[i];
        var child = obj[key];

        if (skipNulls && child === null) {
            continue;
        }

        var childPrefix;
        if (objIsArray) {
            childPrefix = typeof generateArrayPrefix === 'function'
                ? generateArrayPrefix(prefix, key)
                : prefix;
        } else {
            childPrefix = prefix + (allowDots ? '.' + key : '[' + key + ']');
        }

        pushToArray(values, stringify(
            child,
            childPrefix,
            generateArrayPrefix,
            strictNullHandling,
            skipNulls,
            encoder,
            filter,
            sort,
            allowDots,
            serializeDate,
            formatter,
            encodeValuesOnly,
            charset
        ));
    }

    return values;
};
```
