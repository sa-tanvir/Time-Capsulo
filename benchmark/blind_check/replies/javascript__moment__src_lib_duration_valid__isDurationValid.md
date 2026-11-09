```javascript
export default function isDurationValid(m) {
    for (var key in m) {
        if (indexOf.call(ordering, key) === -1) {
            return false;
        }
        var v = m[key];
        if (v != null && isNaN(v)) {
            return false;
        }
    }

    var unitHasDecimal = false;
    for (var i = 0; i < ordering.length; ++i) {
        var value = m[ordering[i]];
        if (value) {
            if (unitHasDecimal) {
                return false;
            }
            if (parseFloat(value) !== toInt(value)) {
                unitHasDecimal = true;
            }
        }
    }

    return true;
}
```
