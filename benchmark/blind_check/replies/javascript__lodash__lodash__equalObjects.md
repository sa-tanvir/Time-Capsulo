```javascript
function equalObjects(object, other, bitmask, customizer, equalFunc, stack) {
    var isPartial = bitmask & COMPARE_PARTIAL_FLAG,
        objProps = getAllKeys(object),
        objLength = objProps.length;

    if (!isPartial) {
      var othProps = getAllKeys(other);
      if (objLength != othProps.length) {
        return false;
      }
    }
    var index = -1;
    while (++index < objLength) {
      var key = objProps[index];
      if (!(isPartial ? key in other : hasOwnProperty.call(other, key))) {
        return false;
      }
    }

    var objStacked = stack.get(object);
    var othStacked = stack.get(other);
    if (objStacked && othStacked) {
      return objStacked == other;
    }

    var result = true,
        skipCtor = false;

    stack.set(object, other);
    stack.set(other, object);

    index = -1;
    while (++index < objLength) {
      key = objProps[index];
      var objValue = object[key],
          othValue = other[key];

      if (key === 'constructor') {
        skipCtor = true;
      }

      var compared;
      if (customizer) {
        compared = isPartial
          ? customizer(othValue, objValue, key, other, object, stack)
          : customizer(objValue, othValue, key, object, other, stack);
      }
      var equal = compared === undefined
        ? (objValue === othValue || equalFunc(objValue, othValue, bitmask, customizer, stack))
        : compared;

      if (!equal) {
        result = false;
        break;
      }
    }

    if (result && !isPartial && !skipCtor) {
      var objCtor = object.constructor,
          othCtor = other.constructor;

      if (objCtor != othCtor &&
          ('constructor' in object && 'constructor' in other) &&
          !(typeof objCtor == 'function' && objCtor instanceof objCtor &&
            typeof othCtor == 'function' && othCtor instanceof othCtor)) {
        result = false;
      }
    }

    stack['delete'](object);
    stack['delete'](other);
    return result;
}
```
