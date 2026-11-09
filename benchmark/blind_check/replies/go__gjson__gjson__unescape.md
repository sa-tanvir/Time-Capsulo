```go
func unescape(json string) string {
	var str = make([]byte, 0, len(json))
	for i := 0; i < len(json); i++ {
		switch {
		default:
			str = append(str, json[i])
		case json[i] < ' ':
			return string(str)
		case json[i] == '\\':
			i++
			if i >= len(json) {
				return string(str)
			}
			switch json[i] {
			default:
				return string(str)
			case '\\':
				str = append(str, '\\')
			case '/':
				str = append(str, '/')
			case 'b':
				str = append(str, '\b')
			case 'f':
				str = append(str, '\f')
			case 'n':
				str = append(str, '\n')
			case 'r':
				str = append(str, '\r')
			case 't':
				str = append(str, '\t')
			case '"':
				str = append(str, '"')
			case 'u':
				if i+5 > len(json) {
					return string(str)
				}
				r := runeit(json[i+1:])
				i += 5 // i now points just past the 4 hex digits
				if utf16.IsSurrogate(r) {
					if len(json)-i >= 6 && json[i] == '\\' && json[i+1] == 'u' {
						r = utf16.DecodeRune(r, runeit(json[i+2:]))
						i += 6
					} else {
						r = utf8.RuneError
					}
				}
				var buf [utf8.UTFMax]byte
				n := utf8.EncodeRune(buf[:], r)
				str = append(str, buf[:n]...)
				i-- // compensate for the loop increment
			}
		}
	}
	return string(str)
}
```
