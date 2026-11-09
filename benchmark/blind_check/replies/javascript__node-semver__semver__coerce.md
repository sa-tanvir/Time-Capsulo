```javascript
function coerce (version, options) {
  if (version instanceof SemVer) {
    return version
  }

  if (typeof version === 'number') {
    version = String(version)
  }

  if (typeof version !== 'string') {
    return null
  }

  options = options || {}

  var match = null
  if (!options.rtl) {
    match = version.match(re[t.COERCE])
  } else {
    // Find the right-most coercible match that does not share its end with
    // a match further to the left, e.g. '1.2.3.4' -> '2.3.4'.
    var rtl = re[t.COERCERTL]
    rtl.lastIndex = 0
    var next
    while ((next = rtl.exec(version)) &&
      (!match || match.index + match[0].length !== version.length)) {
      if (!match ||
          next.index + next[0].length !== match.index + match[0].length) {
        match = next
      }
      // Restart right after the major of this match, so that every digit run
      // (including minor/patch components) is tried as a major.
      rtl.lastIndex = next.index + next[1].length + next[2].length
    }
    // Leave the shared global regex in a clean state.
    rtl.lastIndex = 0
  }

  if (match === null) {
    return null
  }

  return parse(match[2] +
    '.' + (match[3] || '0') +
    '.' + (match[4] || '0'), options)
}
```
