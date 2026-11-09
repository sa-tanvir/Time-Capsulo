```go
func BigComma(b *big.Int) string {
	s := b.String()
	sign := ""
	if len(s) > 0 && s[0] == '-' {
		sign = "-"
		s = s[1:]
	}
	n := len(s)
	if n <= 3 {
		return sign + s
	}
	var buf bytes.Buffer
	buf.Grow(len(sign) + n + (n-1)/3)
	buf.WriteString(sign)
	first := n % 3
	if first == 0 {
		first = 3
	}
	buf.WriteString(s[:first])
	for i := first; i < n; i += 3 {
		buf.WriteByte(',')
		buf.WriteString(s[i : i+3])
	}
	return buf.String()
}
```
