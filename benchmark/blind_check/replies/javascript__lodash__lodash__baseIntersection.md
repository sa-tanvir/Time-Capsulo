```javascript
function baseIntersection(arrays, iteratee, comparator) {
    var othLength = arrays.length,
        first = arrays[0],
        length = first == null ? 0 : first.length,
        maxLength = length,
        others = Array(othLength),
        result = [];

    var othIndex = othLength;
    while (--othIndex > 0) {
      var array = arrays[othIndex];
      var arrLength = array == null ? 0 : array.length;
      if (arrLength < maxLength) {
        maxLength = arrLength;
      }
      if (comparator) {
        others[othIndex] = array;
      } else {
        var cache = new SetCache();
        for (var i = 0; i < arrLength; i++) {
          var v = array[i];
          cache.add(iteratee ? iteratee(v) : v);
        }
        others[othIndex] = cache;
      }
    }

    if (!length || !maxLength) {
      return result;
    }

    var seen = comparator ? null : new SetCache();
    var index = -1;

    outer:
    while (++index < length && result.length < maxLength) {
      var value = first[index];
      var computed = iteratee ? iteratee(value) : value;

      if (comparator) {
        for (var r = 0; r < result.length; r++) {
          if (comparator(computed, result[r])) {
            continue outer;
          }
        }
        for (var o = 1; o < othLength; o++) {
          var oth = others[o];
          var othLen = oth == null ? 0 : oth.length;
          var found = false;
          for (var j = 0; j < othLen; j++) {
            if (comparator(computed, oth[j])) {
              found = true;
              break;
            }
          }
          if (!found) {
            continue outer;
          }
        }
        result.push(value);
      } else {
        if (seen.has(computed)) {
          continue;
        }
        for (var p = 1; p < othLength; p++) {
          if (!others[p].has(computed)) {
            continue outer;
          }
        }
        seen.add(computed);
        result.push(value === 0 ? 0 : value);
      }
    }
    return result;
}
```
