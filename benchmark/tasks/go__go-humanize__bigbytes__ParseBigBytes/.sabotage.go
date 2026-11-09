func ParseBigBytes(s string) (*big.Int, error) {
    panic("TC_STUB")

	lastDigit := 0
	hasComma := false
	for _, r := range s {
		if !(unicode.IsDigit(r) || r == '.' || r == ',') {
			break
		}
		if r == ',' {
			hasComma = true
		}
		lastDigit++
	}

	num := s[:lastDigit]
	if hasComma {
		num = strings.Replace(num, ",", "", -1)
	}

	val := &big.Rat{}
	_, err := fmt.Sscanf(num, "%f", val)
	if err != nil {
		return nil, err
	}

	extra := strings.ToLower(strings.TrimSpace(s[lastDigit:]))
	if m, ok := bigBytesSizeTable[extra]; ok {
		mv := (&big.Rat{}).SetInt(m)
		val.Mul(val, mv)
		rv := &big.Int{}
		rv.Div(val.Num(), val.Denom())
		return rv, nil
	}

	return nil, fmt.Errorf("unhandled size name: %v", extra)
}
