```go
func squash(json string) string {
	if len(json) == 0 {
		return json
	}
	if json[0] == '"' {
		for i := 1; i < len(json); i++ {
			if json[i] == '\\' {
				i++
			} else if json[i] == '"' {
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
				} else if json[i] == '"' {
					break
				}
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
