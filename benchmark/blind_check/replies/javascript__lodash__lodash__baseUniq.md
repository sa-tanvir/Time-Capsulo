```javascript
function baseUniq(array, iteratee, comparator) {
    var index = -1,
        length = array == null ? 0 : array.length,
        result = [];

    if (!length) {
      return result;
    }

    if (comparator) {
      outer:
      while (++index < length) {
        var value = array[index];
        var computed = iteratee ? iteratee(value) : value;
        var resLength = result.length;
        for (var i = 0; i < resLength; i++) {
          if (comparator(computed, result[i])) {
            continue outer;
          }
        }
        result.push(value);
      }
      return result;
    }

    var seen = new SetCache();
    while (++index < length) {
      var value = array[index];
      var computed = iteratee ? iteratee(value) : value;
      if (!seen.has(computed)) {
        seen.add(computed);
        result.push(value === 0 ? 0 : value);
      }
    }
    return result;
}
```
