```go
func stripTrailingZeros(s string) string {
	dot := strings.IndexByte(s, '.')
	if dot < 0 {
		return s
	}
	end := len(s)
	for end > dot+1 && s[end-1] == '0' {
		end--
	}
	if end == dot+1 {
		end = dot
	}
	return s[:end]
}
```
