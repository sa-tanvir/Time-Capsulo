```javascript
export default function isFQDN(str, options) {
  assertString(str);
  options = merge(options, default_fqdn_options);

  let s = String(str);

  /* Remove the optional trailing dot before checking validity */
  if (options.allow_trailing_dot && s[s.length - 1] === '.') {
    s = s.substring(0, s.length - 1);
  }

  const parts = s.split('.');
  for (let i = 0; i < parts.length; i++) {
    if (parts[i].length > 63) {
      return false;
    }
  }

  if (options.require_tld) {
    const tld = parts.pop();
    if (!parts.length || !/^([a-z¡-￿]{2,}|xn[a-z0-9-]{2,})$/i.test(tld)) {
      return false;
    }
    // disallow spaces and special unicode whitespace / invisible characters
    if (/[\s -​  　﻿󠀠]/.test(tld)) {
      return false;
    }
  }

  for (let i = 0; i < parts.length; i++) {
    let part = parts[i];
    if (options.allow_underscores) {
      part = part.replace(/_/g, '');
    }
    if (!/^[a-z¡-￿0-9-]+$/i.test(part)) {
      return false;
    }
    // disallow full-width chars
    if (/[！-～]/.test(part)) {
      return false;
    }
    if (part[0] === '-' || part[part.length - 1] === '-') {
      return false;
    }
  }
  return true;
}
```
