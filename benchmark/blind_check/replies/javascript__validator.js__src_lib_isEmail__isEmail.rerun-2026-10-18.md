```javascript
export default function isEmail(str, options) {
  assertString(str);
  options = merge(options, default_email_options);

  let address = String(str);

  if (options.require_display_name || options.allow_display_name) {
    const display_email = address.match(splitNameAddress);
    if (display_email) {
      let display_name = display_email[1];
      address = display_email[2];
      if (display_name.endsWith(' ')) {
        display_name = display_name.slice(0, -1);
      }
      if (!validateDisplayName(display_name)) {
        return false;
      }
    } else if (options.require_display_name) {
      return false;
    }
  }

  if (!options.ignore_max_length && address.length > defaultMaxEmailLength) {
    return false;
  }

  const atIndex = address.lastIndexOf('@');
  const domain = atIndex === -1 ? address : address.slice(atIndex + 1);
  let user = atIndex === -1 ? '' : address.slice(0, atIndex);
  const lower_domain = domain.toLowerCase();

  if (options.domain_specific_validation && (lower_domain === 'gmail.com' || lower_domain === 'googlemail.com')) {
    user = user.toLowerCase();
    const username = user.split('+')[0];
    if (!isByteLength(username.replace('.', ''), { min: 6, max: 30 })) {
      return false;
    }
    const gmail_parts = username.split('.');
    for (let i = 0; i < gmail_parts.length; i++) {
      if (!gmailUserPart.test(gmail_parts[i])) {
        return false;
      }
    }
  }

  if (!isByteLength(user, { max: 64 }) || !isByteLength(domain, { max: 254 })) {
    return false;
  }

  if (!isFQDN(domain, { require_tld: options.require_tld })) {
    if (!options.allow_ip_domain) {
      return false;
    }
    if (!isIP(domain)) {
      if (!domain.startsWith('[') || !domain.endsWith(']')) {
        return false;
      }
      const noBracketDomain = domain.slice(1, -1);
      if (noBracketDomain.length === 0 || !isIP(noBracketDomain)) {
        return false;
      }
    }
  }

  if (user[0] === '"') {
    const inner = user.slice(1, user.length - 1);
    return options.allow_utf8_local_part ?
      quotedEmailUserUtf8.test(inner) :
      quotedEmailUser.test(inner);
  }

  const pattern = options.allow_utf8_local_part ? emailUserUtf8Part : emailUserPart;
  const user_parts = user.split('.');
  for (let i = 0; i < user_parts.length; i++) {
    if (!pattern.test(user_parts[i])) {
      return false;
    }
  }

  return true;
}
```
