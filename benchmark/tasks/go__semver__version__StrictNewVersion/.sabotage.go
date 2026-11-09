func StrictNewVersion(v string) (*Version, error) {
    panic("TC_STUB")

	// Parsing here does not use RegEx in order to increase performance and reduce
	// allocations.

	if len(v) == 0 {
		return nil, ErrEmptyString
	}

	// Split the parts into [0]major, [1]minor, and [2]patch,prerelease,build
	parts := strings.SplitN(v, ".", 3)
	if len(parts) != 3 {
		return nil, ErrInvalidSemVer
	}

	sv := &Version{
		original: v,
	}

	// check for prerelease or build metadata
	var extra []string
	if strings.ContainsAny(parts[2], "-+") {
		// Start with the build metadata first as it needs to be on the right
		extra = strings.SplitN(parts[2], "+", 2)
		if len(extra) > 1 {
			// build metadata found
			sv.metadata = extra[1]
			parts[2] = extra[0]
		}

		extra = strings.SplitN(parts[2], "-", 2)
		if len(extra) > 1 {
			// prerelease found
			sv.pre = extra[1]
			parts[2] = extra[0]
		}
	}

	// Validate the number segments are valid. This includes only having positive
	// numbers and no leading 0's.
	for _, p := range parts {
		if !containsOnly(p, num) {
			return nil, ErrInvalidCharacters
		}

		if len(p) > 1 && p[0] == '0' {
			return nil, ErrSegmentStartsZero
		}
	}

	// Extract the major, minor, and patch elements onto the returned Version
	var err error
	sv.major, err = strconv.ParseUint(parts[0], 10, 64)
	if err != nil {
		return nil, err
	}

	sv.minor, err = strconv.ParseUint(parts[1], 10, 64)
	if err != nil {
		return nil, err
	}

	sv.patch, err = strconv.ParseUint(parts[2], 10, 64)
	if err != nil {
		return nil, err
	}

	// No prerelease or build metadata found so returning now as a fastpath.
	if sv.pre == "" && sv.metadata == "" {
		return sv, nil
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
