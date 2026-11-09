func NewConstraint(c string) (*Constraints, error) {
    panic("TC_STUB")


	// Rewrite - ranges into a comparison operation.
	c = rewriteRange(c)

	ors := strings.Split(c, "||")
	or := make([][]*constraint, len(ors))
	for k, v := range ors {

		// TODO: Find a way to validate and fetch all the constraints in a simpler form

		// Validate the segment
		if !validConstraintRegex.MatchString(v) {
			return nil, fmt.Errorf("improper constraint: %s", v)
		}

		cs := findConstraintRegex.FindAllString(v, -1)
		if cs == nil {
			cs = append(cs, v)
		}
		result := make([]*constraint, len(cs))
		for i, s := range cs {
			pc, err := parseConstraint(s)
			if err != nil {
				return nil, err
			}

			result[i] = pc
		}
		or[k] = result
	}

	o := &Constraints{constraints: or}
	return o, nil
}
