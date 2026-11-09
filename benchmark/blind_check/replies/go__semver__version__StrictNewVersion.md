```go
func StrictNewVersion(v string) (*Version, error) {
	if len(v) == 0 {
		return nil, ErrEmptyString
	}

	// Split into major, minor and tail at the first two dots.
	d1 := strings.IndexByte(v, '.')
	if d1 < 0 {
		return nil, ErrInvalidSemVer
	}
	d2 := strings.IndexByte(v[d1+1:], '.')
	if d2 < 0 {
		return nil, ErrInvalidSemVer
	}
	d2 += d1 + 1

	majorStr := v[:d1]
	minorStr := v[d1+1 : d2]
	tail := v[d2+1:]

	var pre, metadata string
	if i := strings.IndexByte(tail, '+'); i >= 0 {
		metadata = tail[i+1:]
		tail = tail[:i]
	}
	if i := strings.IndexByte(tail, '-'); i >= 0 {
		pre = tail[i+1:]
		tail = tail[:i]
	}
	patchStr := tail

	for _, p := range [3]string{majorStr, minorStr, patchStr} {
		for i := 0; i < len(p); i++ {
			if p[i] < '0' || p[i] > '9' {
				return nil, ErrInvalidCharacters
			}
		}
		if len(p) > 1 && p[0] == '0' {
			return nil, ErrSegmentStartsZero
		}
	}

	sv := &Version{
		pre:      pre,
		metadata: metadata,
		original: v,
	}

	var err error
	sv.major, err = strconv.ParseUint(majorStr, 10, 64)
	if err != nil {
		return nil, err
	}
	sv.minor, err = strconv.ParseUint(minorStr, 10, 64)
	if err != nil {
		return nil, err
	}
	sv.patch, err = strconv.ParseUint(patchStr, 10, 64)
	if err != nil {
		return nil, err
	}

	if sv.pre != "" {
		if err = validatePrerelease(sv.pre); err != nil {
			return nil, err
		}
	}

	if sv.metadata != "" {
		if err = validateMetadata(sv.metadata); err != nil {
			return nil, err
		}
	}

	return sv, nil
}
```
