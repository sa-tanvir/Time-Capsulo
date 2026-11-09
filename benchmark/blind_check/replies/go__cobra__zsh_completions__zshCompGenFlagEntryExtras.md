```go
func zshCompGenFlagEntryExtras(f *pflag.Flag) string {
	if f.NoOptDefVal != "" {
		return ""
	}

	extras := ":"
	if values, ok := f.Annotations[BashCompFilenameExt]; ok {
		var b strings.Builder
		b.WriteString(":filename:_files")
		for _, pattern := range values {
			b.WriteString(` -g "`)
			b.WriteString(pattern)
			b.WriteString(`"`)
		}
		extras = b.String()
	} else if values, ok := f.Annotations[zshCompDirname]; ok && len(values) > 0 {
		extras = fmt.Sprintf(":filename:_files -g %q", values[0])
	}

	return extras
}
```
