```go
func parseSubSelectors(path string) (sels []subSelector, out string, ok bool) {
	modifier := false
	depth := 1
	colon := 0
	start := 1
	pushSel := func(end int) {
		var sel subSelector
		if colon == 0 {
			sel.path = path[start:end]
		} else {
			sel.name = path[start:colon]
			sel.path = path[colon+1 : end]
		}
		sels = append(sels, sel)
		colon = 0
		start = end + 1
	}
	for i := 1; i < len(path); i++ {
		switch path[i] {
		case '\\':
			i++
		case '@':
			if !modifier && (path[i-1] == '.' || path[i-1] == '|') {
				modifier = true
			}
		case ':':
			if !modifier && colon == 0 && depth == 1 {
				colon = i
			}
		case ',':
			if depth == 1 {
				pushSel(i)
			}
		case '"':
			i++
			for ; i < len(path); i++ {
				if path[i] == '\\' {
					i++
				} else if path[i] == '"' {
					break
				}
			}
		case '[', '(', '{':
			depth++
		case ']', ')', '}':
			depth--
			if depth == 0 {
				pushSel(i)
				return sels, path[i+1:], true
			}
		}
	}
	return sels, "", false
}
```
