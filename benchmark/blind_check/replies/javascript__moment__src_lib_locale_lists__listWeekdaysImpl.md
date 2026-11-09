```javascript
function listWeekdaysImpl (localeSorted, format, index, field) {
    if (typeof localeSorted === 'boolean') {
        if (isNumber(format)) {
            index = format;
            format = undefined;
        }
        format = format || '';
    } else {
        index = localeSorted;
        format = (!isNumber(localeSorted) && localeSorted) ? localeSorted : '';
        localeSorted = false;
    }

    var shift = localeSorted === true ? getLocale()._week.dow : 0;

    if (index != null) {
        return get(format, (index + shift) % 7, field, 'day');
    }

    var out = [];
    for (var i = 0; i < 7; i++) {
        out[i] = get(format, (i + shift) % 7, field, 'day');
    }
    return out;
}
```
