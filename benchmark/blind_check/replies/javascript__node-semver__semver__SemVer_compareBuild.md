```javascript
SemVer.prototype.compareBuild = function (other) {
  if (!(other instanceof SemVer)) {
    other = new SemVer(other, this.options)
  }

  var ab = this.build
  var bb = other.build
  var i = 0
  while (true) {
    var a = ab[i]
    var b = bb[i]
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
