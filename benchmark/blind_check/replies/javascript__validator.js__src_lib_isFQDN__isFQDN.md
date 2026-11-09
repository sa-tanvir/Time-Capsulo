```javascript
export default function isFQDN(str, options) {
  assertString(str);
  options = merge(options, default_fqdn_options);

  /* Remove the optional trailing dot before checking validity */
  if (options.allow_trailing_dot && str[str.length - 1] === '.') {
    str = str.substring(0, str.length - 1);
  }

  const parts = str.split('.');

  for (let i = 0; i < parts.length; i++) {
    if (parts[i].length > 63) {
      return false;
    }
  }

  let labelCount = parts.length;

  if (options.require_tld) {
    if (parts.length < 2) {
      return false;
    }
    const tld = parts[parts.length - 1];

    if (!/^([a-z¡-￿]{2,}|xn[a-z0-9-]{2,})$/i.test(tld)) {
      return false;
    }

    // disallow spaces and other invisible / special characters
    if (/[\s -​  　﻿󠀠]/.test(tld)) {
      return false;
    }

    labelCount = parts.length - 1;
  }

  for (let i = 0; i < labelCount; i++) {
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
