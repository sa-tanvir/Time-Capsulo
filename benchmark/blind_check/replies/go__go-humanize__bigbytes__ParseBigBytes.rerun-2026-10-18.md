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
	num := strings.Replace(s[:lastDigit], ",", "", -1)

	digits := make([]byte, 0, len(num))
	dots := 0
	fracLen := 0
	for i := 0; i < len(num); i++ {
		c := num[i]
		if c == '.' {
			dots++
			continue
		}
		digits = append(digits, c)
		if dots > 0 {
			fracLen++
		}
	}
	if dots > 1 || len(digits) == 0 {
		return nil, fmt.Errorf("invalid number: %q", s[:lastDigit])
	}

	numer, ok := new(big.Int).SetString(string(digits), 10)
	if !ok {
		return nil, fmt.Errorf("invalid number: %q", s[:lastDigit])
	}

	extra := strings.ToLower(strings.TrimSpace(s[lastDigit:]))
	m, found := bigBytesSizeTable[extra]
	if !found {
		return nil, fmt.Errorf("unhandled size name: %v", extra)
	}

	numer.Mul(numer, m)
	if fracLen > 0 {
		denom := new(big.Int).Exp(ten, big.NewInt(int64(fracLen)), nil)
		numer.Quo(numer, denom)
	}
	return numer, nil
}
```
