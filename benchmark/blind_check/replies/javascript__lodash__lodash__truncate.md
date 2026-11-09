```javascript
function truncate(string, options) {
    var length = DEFAULT_TRUNC_LENGTH,
        omission = DEFAULT_TRUNC_OMISSION,
        separator;

    if (isObject(options)) {
      if ('separator' in options) {
        separator = options.separator;
      }
      if ('length' in options) {
        length = toInteger(options.length);
      }
      if ('omission' in options) {
        omission = baseToString(options.omission);
      }
    }
    string = toString(string);

    var strSymbols,
        strLength = string.length;

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
    var cut = result.length;

    if (isRegExp(separator)) {
      var remainder = string.slice(cut);
      var flags = reFlags.exec(String(separator))[0];
      if (flags.indexOf('g') < 0) {
        flags += 'g';
      }
      var globalSep = new RegExp(separator.source, flags);
      globalSep.lastIndex = 0;
      var firstMatch = globalSep.exec(remainder);
      if (!firstMatch || firstMatch.index > 0) {
        var newEnd,
            match;
        globalSep.lastIndex = 0;
        while ((match = globalSep.exec(result))) {
          newEnd = match.index;
          if (match[0] === '') {
            globalSep.lastIndex++;
          }
        }
        if (newEnd !== undefined) {
          result = result.slice(0, newEnd);
        }
      }
    } else {
      separator = baseToString(separator);
      if (string.indexOf(separator, cut) != cut) {
        var index = result.lastIndexOf(separator);
        if (index > -1) {
          result = result.slice(0, index);
        }
      }
    }
    return result + omission;
}
```
