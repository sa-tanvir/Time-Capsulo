```go
func comparePrerelease(v, o string) int {
	vDone, oDone := false, false
	for !vDone || !oDone {
		var a, b string
		if !vDone {
			if k := strings.IndexByte(v, '.'); k >= 0 {
				a, v = v[:k], v[k+1:]
			} else {
				a, vDone = v, true
			}
		}
		if !oDone {
			if k := strings.IndexByte(o, '.'); k >= 0 {
				b, o = o[:k], o[k+1:]
			} else {
				b, oDone = o, true
			}
		}
		if a != b {
			if c := comparePrePart(a, b); c != 0 {
				return c
			}
		}
	}
	return 0
}
```
