```go
func parseQuery(query string) (
	path, op, value, remain string, i int, ok bool,
) {
	if len(query) < 2 || query[0] != '#' ||
		(query[1] != '(' && query[1] != '[') {
		return "", "", "", "", i, false
	}
	i = 2
	j := 0 // start of value part (operator start)
	depth := 1
	for ; i < len(query); i++ {
		c := query[i]
		if depth == 1 && j == 0 {
			switch c {
			case '!', '=', '<', '>', '%':
				// start of the value part
				j = i
				continue
			}
		}
		if c == '\\' {
			i++
		} else if c == '[' || c == '(' {
			depth++
		} else if c == ']' || c == ')' {
			depth--
			if depth == 0 {
				break
			}
		} else if c == '"' {
			// inside selector string, balance quotes
			i++
			for ; i < len(query); i++ {
				if query[i] == '\\' {
					i++
				} else if query[i] == '"' {
					break
				}
			}
		}
	}
	if depth > 0 {
		return "", "", "", "", i, false
	}
	if j > 0 {
		path = trim(query[2:j])
		v := trim(query[j:i])
		if len(v) == 1 {
			op = v
			value = ""
		} else if len(v) >= 2 {
			switch v[:2] {
			case "!=", "!%", "<=", ">=":
				op = v[:2]
				value = v[2:]
			case "==":
				op = "="
				value = v[2:]
			default:
				switch v[0] {
				case '<', '>', '=', '%':
					op = v[:1]
					value = v[1:]
				default:
					op = ""
					value = v
				}
			}
			value = trim(value)
		}
	} else {
		path = trim(query[2:i])
	}
	remain = query[i+1:]
	return path, op, value, remain, i + 1, true
}
```
