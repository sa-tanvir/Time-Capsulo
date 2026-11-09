func zshCompRenderZshCompArgHint(i int, z zshCompArgHint) (string, error) {
	switch t := z.Tipe; t {
	case zshCompArgumentFilenameComp:
		var globs []string
		for _, g := range z.Options {
			globs = append(globs, fmt.Sprintf(`-g "%s"`, g))
		}
		return fmt.Sprintf(`'%d: :_files %s'`, i, strings.Join(globs, " ")), nil
	case zshCompArgumentWordComp:
		var words []string
		for _, w := range z.Options {
			words = append(words, fmt.Sprintf("%q", w))
		}
		return fmt.Sprintf(`'%d: :(%s)'`, i, strings.Join(words, " ")), nil
	default:
		return "", fmt.Errorf("Invalid zsh argument completion annotation: %s", t)
	}
}
