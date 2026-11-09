```go
func Commaf(v float64) string {
	var buf bytes.Buffer
	if v < 0 {
		buf.WriteByte('-')
		v = -v
	}
	s := strconv.FormatFloat(v, 'f', -1, 64)
	if len(s) > 0 && s[0] == '-' {
		// negative zero
		buf.WriteByte('-')
		s = s[1:]
	}
	intPart, frac := s, ""
	if i := strings.IndexByte(s, '.'); i >= 0 {
		intPart, frac = s[:i], s[i:]
	}
	n := len(intPart)
	buf.Grow(n + n/3 + len(frac))
	first := n % 3
	if first == 0 {
		first = 3
	}
	if first > n {
		first = n
	}
	buf.WriteString(intPart[:first])
	for i := first; i < n; i += 3 {
		buf.WriteByte(',')
		buf.WriteString(intPart[i : i+3])
	}
	buf.WriteString(frac)
	return buf.String()
}
```
