```javascript
const isValidDate = (str) => {
  const isLeap = y => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;

  // str must have passed the ISO8601 check
  // this check is meant to catch invalid dates
  // like 2009-02-31
  // first check for ordinal dates
  const ordinalMatch = str.match(/^(\d{4})-?(\d{3})([ T]|$)/);
  if (ordinalMatch) {
    const oYear = Number(ordinalMatch[1]);
    const oDay = Number(ordinalMatch[2]);
    return oDay <= (isLeap(oYear) ? 366 : 365);
  }

  const match = str.match(/(\d{4})-?(\d{0,2})-?(\d*)/);
  if (!match) {
    return true;
  }
  const year = Number(match[1]);
  const month = match[2] ? Number(match[2]) : 0;
  const day = match[3] ? Number(match[3]) : 0;

  if (month && day) {
    if (month < 1 || month > 12) {
      return false;
    }
    const monthLengths = [31, isLeap(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    return day >= 1 && day <= monthLengths[month - 1];
  }

  return true;
}
```
