const isValidDate = (str) => {
  // str must have passed the ISO8601 check
  // this check is meant to catch invalid dates
  // like 2009-02-31
  // first check for ordinal dates
  const ordinalMatch = str.match(/^(\d{4})-?(\d{3})([ T]{1}\.*|$)/);
  if (ordinalMatch) {
    const oYear = Number(ordinalMatch[1]);
    const oDay = Number(ordinalMatch[2]);
    // if is leap year
    if ((oYear % 4 === 0 && oYear % 100 !== 0) || oYear % 400 === 0) return oDay <= 366;
    return oDay <= 365;
  }
  const match = str.match(/(\d{4})-?(\d{0,2})-?(\d*)/).map(Number);
  const year = match[1];
  const month = match[2];
  const day = match[3];
  const monthString = month ? `0${month}`.slice(-2) : month;
  const dayString = day ? `0${day}`.slice(-2) : day;

  // create a date object and compare
  const d = new Date(`${year}-${monthString || '01'}-${dayString || '01'}`);
  if (month && day) {
    return d.getUTCFullYear() === year
      && (d.getUTCMonth() + 1) === month
      && d.getUTCDate() === day;
  }
  return true;
}
