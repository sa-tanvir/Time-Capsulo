```go
func ParseBytes(s string) (uint64, error) {
	lastDigit := 0
	hasComma := false
	for lastDigit < len(s) {
		c := s[lastDigit]
		if (c >= '0' && c <= '9') || c == '.' || c == ',' {
			if c == ',' {
				hasComma = true
			}
			lastDigit++
			continue
		}
		break
	}
	num := s[:lastDigit]
	if hasComma {
		num = strings.Replace(num, ",", "", -1)
	}

	f, err := strconv.ParseFloat(num, 64)
	if err != nil {
		return 0, err
	}

	extra := strings.ToLower(strings.TrimSpace(s[lastDigit:]))
	if m, ok := bytesSizeTable[extra]; ok {
		f *= float64(m)
		if f >= math.MaxUint64 {
			return 0, fmt.Errorf("too large: %v", s)
		}
		return uint64(f), nil
	}

	return 0, fmt.Errorf("unhandled size name: %v", extra)
}
```
