```go
func ParseBigBytes(s string) (*big.Int, error) {
	lastDigit := 0
	for lastDigit < len(s) {
		c := s[lastDigit]
		if (c >= '0' && c <= '9') || c == '.' || c == ',' {
			lastDigit++
			continue
		}
		break
	}

	// Collect digits (commas ignored), remembering the fractional length.
	digits := make([]byte, 0, lastDigit)
	nDigits := 0
	fracLen := 0
	seenDot := false
	for i := 0; i < lastDigit; i++ {
		c := s[i]
		switch {
		case c == ',':
			// thousands separator, ignored
		case c == '.':
			if seenDot {
				return nil, fmt.Errorf("invalid number: %q", s[:lastDigit])
			}
			seenDot = true
		default:
			digits = append(digits, c)
			nDigits++
			if seenDot {
				fracLen++
			}
		}
	}
	if nDigits == 0 {
		return nil, fmt.Errorf("invalid number: %q", s[:lastDigit])
	}

	extra := strings.ToLower(strings.TrimSpace(s[lastDigit:]))
	m, ok := bigBytesSizeTable[extra]
	if !ok {
		return nil, fmt.Errorf("unhandled size name: %v", extra)
	}

	num, ok := new(big.Int).SetString(string(digits), 10)
	if !ok {
		return nil, fmt.Errorf("invalid number: %q", s[:lastDigit])
	}
	num.Mul(num, m)
	if fracLen > 0 {
		den := new(big.Int).Exp(ten, big.NewInt(int64(fracLen)), nil)
		num.Quo(num, den)
	}
	return num, nil
}
```
