```javascript
function truncate(string, options) {
    var length = DEFAULT_TRUNC_LENGTH,
        omission = DEFAULT_TRUNC_OMISSION,
        separator;

    if (isObject(options)) {
        separator = 'separator' in options ? options.separator : separator;
        length = 'length' in options ? toInteger(options.length) : length;
        omission = 'omission' in options ? baseToString(options.omission) : omission;
    }
    string = toString(string);

    var strLength = string.length,
        strSymbols;
    if (hasUnicode(string)) {
        strSymbols = stringToArray(string);
        strLength = strSymbols.length;
    }
    if (length >= strLength) {
        return string;
    }
    var end = length - stringSize(omission);
    if (end < 1) {
        return omission;
    }
    var result = strSymbols
        ? castSlice(strSymbols, 0, end).join('')
        : string.slice(0, end);

    if (separator === undefined) {
        return result + omission;
    }
    if (strSymbols) {
        end = result.length;
    }
    if (isRegExp(separator)) {
        if (string.slice(end).search(separator)) {
            var match,
                newEnd,
                substring = result;

            if (!separator.global) {
                separator = RegExp(separator.source, toString(reFlags.exec(separator)) + 'g');
            }
            separator.lastIndex = 0;
            while ((match = separator.exec(substring))) {
                newEnd = match.index;
                if (match[0] === '') {
                    separator.lastIndex++;
                }
            }
            result = result.slice(0, newEnd === undefined ? end : newEnd);
        }
    } else if (string.indexOf(baseToString(separator), end) != end) {
        var index = result.lastIndexOf(separator);
        if (index > -1) {
            result = result.slice(0, index);
        }
    }
    return result + omission;
}
```
