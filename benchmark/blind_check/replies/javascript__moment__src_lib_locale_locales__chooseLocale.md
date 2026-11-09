```javascript
function chooseLocale(names) {
    var i = 0, j, next, locale, split, nextName;

    while (i < names.length) {
        split = normalizeLocale(names[i]).split('-');
        j = split.length;
        nextName = i + 1 < names.length ? normalizeLocale(names[i + 1]) : null;
        next = nextName ? nextName.split('-') : null;
        while (j > 0) {
            locale = loadLocale(split.slice(0, j).join('-'));
            if (locale) {
                return locale;
            }
            if (next && next.length >= j && compareArrays(split, next, true) >= j - 1) {
                break;
            }
            j--;
        }
        i++;
    }
    return globalLocale;
}
```
