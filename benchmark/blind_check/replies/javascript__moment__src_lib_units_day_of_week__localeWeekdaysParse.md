```javascript
export function localeWeekdaysParse (weekdayName, format, strict) {
    var i, mom, regex;

    if (this._weekdaysParseExact) {
        return handleStrictParse.call(this, weekdayName, format, strict);
    }

    if (!this._weekdaysParse) {
        this._weekdaysParse = [];
    }
    if (strict) {
        if (!this._fullWeekdaysParse) {
            this._fullWeekdaysParse = [];
        }
        if (!this._shortWeekdaysParse) {
            this._shortWeekdaysParse = [];
        }
        if (!this._minWeekdaysParse) {
            this._minWeekdaysParse = [];
        }
    }

    for (i = 0; i < 7; i++) {
        mom = createUTC([2000, 1]).day(i);

        if (strict && !this._fullWeekdaysParse[i]) {
            this._fullWeekdaysParse[i] = new RegExp('^' + this.weekdays(mom, '').replace('.', '\\.?') + '$', 'i');
            this._shortWeekdaysParse[i] = new RegExp('^' + this.weekdaysShort(mom, '').replace('.', '\\.?') + '$', 'i');
            this._minWeekdaysParse[i] = new RegExp('^' + this.weekdaysMin(mom, '').replace('.', '\\.?') + '$', 'i');
        }
        if (!this._weekdaysParse[i]) {
            regex = '^' + this.weekdays(mom, '') + '|^' + this.weekdaysShort(mom, '') + '|^' + this.weekdaysMin(mom, '');
            this._weekdaysParse[i] = new RegExp(regex.replace('.', ''), 'i');
        }

        if (strict) {
            if (format === 'dddd' && this._fullWeekdaysParse[i].test(weekdayName)) {
                return i;
            } else if (format === 'ddd' && this._shortWeekdaysParse[i].test(weekdayName)) {
                return i;
            } else if (format === 'dd' && this._minWeekdaysParse[i].test(weekdayName)) {
                return i;
            }
        } else if (this._weekdaysParse[i].test(weekdayName)) {
            return i;
        }
    }
}
```
