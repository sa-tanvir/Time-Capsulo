```go
func squash(json string) string {
	if len(json) == 0 {
		return json
	}
	if json[0] == '"' {
		for i := 1; i < len(json); i++ {
			switch json[i] {
			case '\\':
				i++
			case '"':
				return json[:i+1]
			}
		}
		return json
	}
	depth := 1
	for i := 1; i < len(json); i++ {
		switch json[i] {
		case '"':
			i++
			for ; i < len(json); i++ {
				if json[i] == '\\' {
					i++
					continue
				}
				if json[i] == '"' {
					break
				}
			}
			if i >= len(json) {
				return json
			}
		case '[', '{', '(':
			depth++
		case ']', '}', ')':
			depth--
			if depth == 0 {
				return json[:i+1]
			}
		}
	}
	return json
}
```
