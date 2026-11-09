```javascript
Range.prototype.parseRange = function (range) {
  var loose = this.options.loose
  var options = this.options
  range = range.trim()
  // `1.2.3 - 1.2.4` => `>=1.2.3 <=1.2.4`
  var hr = loose ? re[t.HYPHENRANGELOOSE] : re[t.HYPHENRANGE]
  range = range.replace(hr, hyphenReplace)
  // `> 1.2.3 < 1.2.5` => `>1.2.3 <1.2.5`
  range = range.replace(re[t.COMPARATORTRIM], comparatorTrimReplace)
  // `~ 1.2.3` => `~1.2.3`
  range = range.replace(re[t.TILDETRIM], tildeTrimReplace)
  // `^ 1.2.3` => `^1.2.3`
  range = range.replace(re[t.CARETTRIM], caretTrimReplace)
  // normalize spaces
  range = range.split(/\s+/).join(' ')

  var compRe = loose ? re[t.COMPARATORLOOSE] : re[t.COMPARATOR]
  var set = range.split(' ').map(function (comp) {
    return parseComparator(comp, options)
  }).join(' ').split(/\s+/)
  if (loose) {
    set = set.filter(function (comp) {
      return !!comp.match(compRe)
    })
  }
  return set.map(function (comp) {
    return new Comparator(comp, options)
  })
}
```
