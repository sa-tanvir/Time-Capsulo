```go
func Comma(v int64) string {
	s := strconv.FormatInt(v, 10)
	start := 0
	if v < 0 {
		start = 1
	}
	n := len(s) - start
	if n <= 3 {
		return s
	}
	out := make([]byte, 0, len(s)+(n-1)/3)
	out = append(out, s[:start]...)
	first := n % 3
	if first == 0 {
		first = 3
	}
	out = append(out, s[start:start+first]...)
	for i := start + first; i < len(s); i += 3 {
		out = append(out, ',')
		out = append(out, s[i:i+3]...)
	}
	return string(out)
}
```
