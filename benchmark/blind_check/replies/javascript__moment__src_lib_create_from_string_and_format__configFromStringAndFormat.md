```javascript
export function configFromStringAndFormat(config) {
    if (config._f === hooks.ISO_8601) {
        configFromISO(config);
        return;
    }
    if (config._f === hooks.RFC_2822) {
        configFromRFC2822(config);
        return;
    }
    config._a = [];
    getParsingFlags(config).empty = true;

    var string = '' + config._i,
        i, token, parsedInput, match, skipped, pos,
        tokens = expandFormat(config._f, config._locale).match(formattingTokens) || [],
        stringLength = string.length,
        totalParsedInputLength = 0;

    for (i = 0; i < tokens.length; i++) {
        token = tokens[i];
        match = string.match(getParseRegexForToken(token, config));
        parsedInput = match ? match[0] : undefined;
        if (parsedInput) {
            pos = string.indexOf(parsedInput);
            skipped = string.substr(0, pos);
            if (skipped.length > 0) {
                getParsingFlags(config).unusedInput.push(skipped);
            }
            string = string.slice(pos + parsedInput.length);
            totalParsedInputLength += parsedInput.length;
        }
        if (Object.prototype.hasOwnProperty.call(formatTokenFunctions, token)) {
            if (parsedInput) {
                getParsingFlags(config).empty = false;
            } else {
                getParsingFlags(config).unusedTokens.push(token);
            }
            addTimeToArrayFromToken(token, parsedInput, config);
        } else if (config._strict && !parsedInput) {
            getParsingFlags(config).unusedTokens.push(token);
        }
    }

    getParsingFlags(config).charsLeftOver = stringLength - totalParsedInputLength;
    if (string.length > 0) {
        getParsingFlags(config).unusedInput.push(string);
    }

    if (config._a[HOUR] <= 12 &&
        getParsingFlags(config).bigHour === true &&
        config._a[HOUR] > 0) {
        getParsingFlags(config).bigHour = undefined;
    }

    getParsingFlags(config).parsedDateParts = config._a.slice(0);
    getParsingFlags(config).meridiem = config._meridiem;
    config._a[HOUR] = meridiemFixWrap(config._locale, config._a[HOUR], config._meridiem);

    configFromArray(config);
    checkOverflow(config);
}
```
