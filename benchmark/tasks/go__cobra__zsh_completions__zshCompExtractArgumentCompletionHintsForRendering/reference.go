func zshCompExtractArgumentCompletionHintsForRendering(c *Command) ([]string, error) {
	var result []string
	annotation, err := c.zshCompGetArgsAnnotations()
	if err != nil {
		return nil, err
	}
	for k, v := range annotation {
		s, err := zshCompRenderZshCompArgHint(k, v)
		if err != nil {
			return nil, err
		}
		result = append(result, s)
	}
	if len(c.ValidArgs) > 0 {
		if _, positionOneExists := annotation[1]; !positionOneExists {
			s, err := zshCompRenderZshCompArgHint(1, zshCompArgHint{
				Tipe:    zshCompArgumentWordComp,
				Options: c.ValidArgs,
			})
			if err != nil {
				return nil, err
			}
			result = append(result, s)
		}
	}
	sort.Strings(result)
	return result, nil
}
