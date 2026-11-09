```javascript
function checkHost(host, matches) {
  for (let i = 0; i < matches.length; i++) {
    const match = matches[i];
    if (host === match || (isRegExp(match) && match.test(host))) {
      return true;
    }
  }
  return false;
}
```
