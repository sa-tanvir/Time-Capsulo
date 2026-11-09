```javascript
SemVer.prototype.comparePre = function (other) {
  if (!(other instanceof SemVer)) {
    other = new SemVer(other, this.options)
  }

  var ap = this.prerelease
  var bp = other.prerelease

  // NOT having a prerelease is > having one
  if (ap.length && !bp.length) {
    return -1
  } else if (!ap.length && bp.length) {
    return 1
  } else if (!ap.length && !bp.length) {
    return 0
  }

  var i = 0
  while (true) {
    var a = ap[i]
    var b = bp[i]
    if (a === undefined && b === undefined) {
      return 0
    } else if (b === undefined) {
      return 1
    } else if (a === undefined) {
      return -1
    } else if (a === b) {
      i++
      continue
    } else {
      return compareIdentifiers(a, b)
    }
  }
}
```
