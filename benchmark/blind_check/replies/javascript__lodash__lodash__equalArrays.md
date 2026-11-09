```javascript
function equalArrays(array, other, bitmask, customizer, equalFunc, stack) {
    var isPartial = bitmask & COMPARE_PARTIAL_FLAG,
        isUnordered = bitmask & COMPARE_UNORDERED_FLAG,
        arrLength = array.length,
        othLength = other.length;

    if (arrLength != othLength && !(isPartial && othLength > arrLength)) {
      return false;
    }
    var arrStacked = stack.get(array);
    var othStacked = stack.get(other);
    if (arrStacked && othStacked) {
      return arrStacked == other;
    }

    var index = -1,
        result = true,
        claimed = isUnordered ? [] : null;

    stack.set(array, other);
    stack.set(other, array);

    while (++index < arrLength) {
      var arrValue = array[index],
          othValue = other[index];

      if (customizer) {
        var compared = isPartial
          ? customizer(othValue, arrValue, index, other, array, stack)
          : customizer(arrValue, othValue, index, array, other, stack);

        if (compared !== undefined) {
          if (compared) {
            continue;
          }
          result = false;
          break;
        }
      }

      if (isUnordered) {
        var found = false;
        for (var j = 0; j < othLength; j++) {
          if (claimed[j]) {
            continue;
          }
          var candidate = other[j];
          if (arrValue === candidate ||
              equalFunc(arrValue, candidate, bitmask, customizer, stack)) {
            claimed[j] = true;
            found = true;
            break;
          }
        }
        if (!found) {
          result = false;
          break;
        }
      } else if (!(
            arrValue === othValue ||
            equalFunc(arrValue, othValue, bitmask, customizer, stack)
          )) {
        result = false;
        break;
      }
    }

    stack['delete'](array);
    stack['delete'](other);
    return result;
}
```
