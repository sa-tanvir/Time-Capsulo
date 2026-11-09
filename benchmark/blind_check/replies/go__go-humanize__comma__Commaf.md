```go
func Commaf(v float64) string {
	s := strconv.FormatFloat(v, 'f', -1, 64)
	sign := ""
	if len(s) > 0 && s[0] == '-' {
		sign = "-"
		s = s[1:]
	}
	intPart := s
	frac := ""
	if i := strings.IndexByte(s, '.'); i >= 0 {
		intPart = s[:i]
		frac = s[i:]
	}
	n := len(intPart)
	var buf bytes.Buffer
	buf.Grow(len(sign) + n + n/3 + len(frac))
	buf.WriteString(sign)
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
