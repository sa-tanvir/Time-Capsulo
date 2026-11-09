```go
func comparePrerelease(v, o string) int {
	// Walk both strings identifier by identifier without allocating.
	// vDone / oDone mark lists that are exhausted; missing identifiers
	// count as "".
	vDone, oDone := false, false
	for !vDone || !oDone {
		var a, b string
		if !vDone {
			if i := strings.IndexByte(v, '.'); i >= 0 {
				a, v = v[:i], v[i+1:]
			} else {
				a, vDone = v, true
			}
		}
		if !oDone {
			if i := strings.IndexByte(o, '.'); i >= 0 {
				b, o = o[:i], o[i+1:]
			} else {
				b, oDone = o, true
			}
		}

		if a == b {
			continue
		}
		if a == "" {
			return -1
		}
		if b == "" {
			return 1
		}

		an, aErr := strconv.ParseUint(a, 10, 64)
		bn, bErr := strconv.ParseUint(b, 10, 64)
		aNum, bNum := aErr == nil, bErr == nil

		switch {
		case aNum && bNum:
			if an > bn {
				return 1
			}
			// an < bn, or equal values with differing text (leading zeros).
			return -1
		case aNum:
			return -1
		case bNum:
			return 1
		default:
			if a > b {
				return 1
			}
			return -1
		}
	}
	return 0
}
```
