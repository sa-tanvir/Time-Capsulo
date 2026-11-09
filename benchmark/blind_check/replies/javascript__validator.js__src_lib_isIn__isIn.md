```javascript
export default function isIn(str, options) {
  assertString(str);
  let i;
  if (Object.prototype.toString.call(options) === '[object Array]') {
    for (i = 0; i < options.length; i++) {
      if (toString(options[i]) === str) {
        return true;
      }
    }
    return false;
  } else if (typeof options === 'object') {
    return options.hasOwnProperty(str);
  } else if (options && typeof options.indexOf === 'function') {
    return options.indexOf(str) >= 0;
  }
  return false;
}
```
