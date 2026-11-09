```javascript
function baseDifference(array, values, iteratee, comparator) {
    var length = array == null ? 0 : array.length,
        result = [];

    if (!length) {
      return result;
    }
    var keys = values;
    if (iteratee) {
      keys = arrayMap(values, baseUnary(iteratee));
    }
    var index = -1;

    if (comparator) {
      var valuesLength = values.length;
      while (++index < length) {
        var value = array[index];
        var computed = iteratee ? iteratee(value) : value;
        var found = false;
        for (var j = 0; j < valuesLength; j++) {
          if (comparator(computed, keys[j])) {
            found = true;
            break;
          }
        }
        if (!found) {
          result.push(value);
        }
      }
      return result;
    }

    var keysLength = keys.length;
    var useCache = keysLength >= LARGE_ARRAY_SIZE;
    var cache = useCache ? new SetCache(keys) : null;

    while (++index < length) {
      var value = array[index];
      var computed = iteratee ? iteratee(value) : value;
      var excluded;
      if (useCache) {
        excluded = cacheHas(cache, computed);
      } else if (computed === computed) {
        excluded = false;
        for (var k = 0; k < keysLength; k++) {
          if (keys[k] === computed) {
            excluded = true;
            break;
          }
        }
      } else {
        excluded = false;
        for (var m = 0; m < keysLength; m++) {
          var key = keys[m];
          if (key !== key) {
            excluded = true;
            break;
          }
        }
      }
      if (!excluded) {
        result.push(value === 0 ? 0 : value);
      }
    }
    return result;
}
```
