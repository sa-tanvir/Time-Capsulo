```javascript
export function configFromStringAndArray(config) {
    var tempConfig,
        bestMoment,
        scoreToBeat,
        i,
        currentScore,
        formats = config._f,
        len = formats.length;

    if (len === 0) {
        getParsingFlags(config).invalidFormat = true;
        config._d = new Date(NaN);
        return;
    }

    for (i = 0; i < len; i++) {
        currentScore = 0;
        tempConfig = copyConfig({}, config);
        if (config._useUTC != null) {
            tempConfig._useUTC = config._useUTC;
        }
        // each attempt gets its own fresh parsing flags (copyConfig shares the object)
        delete tempConfig._pf;
        tempConfig._f = formats[i];
        configFromStringAndFormat(tempConfig);

        if (!isValid(tempConfig)) {
            if (i === len - 1 && bestMoment === undefined) {
                bestMoment = tempConfig;
            }
            continue;
        }

        var flags = getParsingFlags(tempConfig);
        currentScore += flags.charsLeftOver;
        currentScore += (flags.unusedTokens ? flags.unusedTokens.length : 0) * 10;
        flags.score = currentScore;

        if (scoreToBeat == null || currentScore < scoreToBeat) {
            scoreToBeat = currentScore;
            bestMoment = tempConfig;
        }
    }

    if (scoreToBeat == null) {
        bestMoment = tempConfig;
    }

    extend(config, bestMoment);
}
```
