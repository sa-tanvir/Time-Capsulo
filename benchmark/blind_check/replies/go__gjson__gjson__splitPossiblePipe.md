```go
func splitPossiblePipe(path string) (left, right string, ok bool) {
	// take a quick peek for the pipe character. If found we'll split the piped
	// part of the path into the left and right side.
	if strings.IndexByte(path, '|') == -1 {
		return "", "", false
	}

	if len(path) > 0 && path[0] == '{' {
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
					open := path[i]
					var close byte = ']'
					if open == '(' {
						close = ')'
					}
					i++
					depth := 1
					for ; i < len(path); i++ {
						c := path[i]
						if c == '\\' {
							i++
						} else if c == open {
							depth++
						} else if c == close {
							depth--
							if depth == 0 {
								break
							}
						} else if c == '"' {
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
