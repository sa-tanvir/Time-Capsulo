```go
func splitPossiblePipe(path string) (left, right string, ok bool) {
	if strings.IndexByte(path, '|') < 0 {
		return "", "", false
	}
	if path[0] == '{' {
		sq := squash(path[1:])
		if len(sq) < len(path)-1 && path[len(sq)+1] == '|' {
			return path[:len(sq)+1], path[len(sq)+2:], true
		}
		return "", "", false
	}
	for i := 0; i < len(path); i++ {
		switch path[i] {
		case '\\':
			i++
		case '|':
			return path[:i], path[i+1:], true
		case '.':
			if i == len(path)-1 {
				return "", "", false
			}
			if path[i+1] == '#' {
				i += 2
				if i == len(path) {
					return "", "", false
				}
				if path[i] == '[' || path[i] == '(' {
					var open, close byte
					if path[i] == '[' {
						open, close = '[', ']'
					} else {
						open, close = '(', ')'
					}
					i++
					depth := 1
				scan:
					for ; i < len(path); i++ {
						switch path[i] {
						case '\\':
							i++
						case open:
							depth++
						case close:
							depth--
							if depth == 0 {
								break scan
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
						}
					}
				}
			}
		}
	}
	return "", "", false
}
```
