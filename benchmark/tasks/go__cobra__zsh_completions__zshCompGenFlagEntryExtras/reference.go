func zshCompGenFlagEntryExtras(f *pflag.Flag) string {
	if f.NoOptDefVal != "" {
		return ""
	}

	extras := ":" // allow options for flag (even without assistance)
	for key, values := range f.Annotations {
		switch key {
		case zshCompDirname:
			extras = fmt.Sprintf(":filename:_files -g %q", values[0])
		case BashCompFilenameExt:
			extras = ":filename:_files"
			for _, pattern := range values {
				extras = extras + fmt.Sprintf(` -g "%s"`, pattern)
			}
		}
	}

	return extras
}
