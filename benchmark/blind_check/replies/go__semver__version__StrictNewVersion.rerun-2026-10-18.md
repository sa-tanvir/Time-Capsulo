```go
func StrictNewVersion(v string) (*Version, error) {
	if len(v) == 0 {
		return nil, ErrEmptyString
	}

	i := strings.IndexByte(v, '.')
	if i < 0 {
		return nil, ErrInvalidSemVer
	}
	j := strings.IndexByte(v[i+1:], '.')
	if j < 0 {
		return nil, ErrInvalidSemVer
	}
	j += i + 1

	majorStr := v[:i]
	minorStr := v[i+1 : j]
	tail := v[j+1:]

	var pre, meta string
	if k := strings.IndexByte(tail, '+'); k >= 0 {
		meta = tail[k+1:]
		tail = tail[:k]
	}
	if k := strings.IndexByte(tail, '-'); k >= 0 {
		pre = tail[k+1:]
		tail = tail[:k]
	}

	parts := [3]string{majorStr, minorStr, tail}
	for _, p := range parts {
		for k := 0; k < len(p); k++ {
			if p[k] < '0' || p[k] > '9' {
				return nil, ErrInvalidCharacters
			}
		}
		if len(p) > 1 && p[0] == '0' {
			return nil, ErrSegmentStartsZero
		}
	}

	var nums [3]uint64
	for k, p := range parts {
		n, err := strconv.ParseUint(p, 10, 64)
		if err != nil {
			return nil, err
		}
		nums[k] = n
	}

	if pre != "" {
		if err := validatePrerelease(pre); err != nil {
			return nil, err
		}
	}
	if meta != "" {
		if err := validateMetadata(meta); err != nil {
			return nil, err
		}
	}

	return &Version{
		major:    nums[0],
		minor:    nums[1],
		patch:    nums[2],
		pre:      pre,
		metadata: meta,
		original: v,
	}, nil
}
```
