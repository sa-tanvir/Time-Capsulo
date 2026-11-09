```go
func indentString(s, p string) string {
	if len(s) == 0 || len(p) == 0 {
		return s
	}
	var b strings.Builder
	b.Grow(len(s) + len(p)*(strings.Count(s, "\n")+1))
	atLineStart := true
	for i := 0; i < len(s); i++ {
		c := s[i]
		if atLineStart && c != '\n' {
			b.WriteString(p)
		}
		b.WriteByte(c)
		atLineStart = c == '\n'
	}
	return b.String()
}
```
