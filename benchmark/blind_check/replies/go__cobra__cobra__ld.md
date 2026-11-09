```go
func ld(s, t string, ignoreCase bool) int {
	if ignoreCase {
		s = strings.ToLower(s)
		t = strings.ToLower(t)
	}
	if len(s) == 0 {
		return len(t)
	}
	if len(t) == 0 {
		return len(s)
	}
	if len(t) > len(s) {
		s, t = t, s
	}
	// t is the shorter string; keep a single row of length len(t)+1.
	row := make([]int, len(t)+1)
	for j := range row {
		row[j] = j
	}
	for i := 1; i <= len(s); i++ {
		prev := row[0] // d[i-1][j-1]
		row[0] = i
		si := s[i-1]
		for j := 1; j <= len(t); j++ {
			cur := row[j] // d[i-1][j]
			cost := 1
			if si == t[j-1] {
				cost = 0
			}
			best := prev + cost
			if v := cur + 1; v < best {
				best = v
			}
			if v := row[j-1] + 1; v < best {
				best = v
			}
			row[j] = best
			prev = cur
		}
	}
	return row[len(t)]
}
```
