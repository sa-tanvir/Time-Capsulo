```go
func matchMapWithRegex(toCheck map[string]*regexp.Regexp, toMatch map[string][]string, canonicalKey bool) bool {
	for k, re := range toCheck {
		if canonicalKey {
			k = http.CanonicalHeaderKey(k)
		}
		values := toMatch[k]
		if values == nil {
			return false
		}
		if re == nil {
			continue
		}
		matched := false
		for _, v := range values {
			if re.MatchString(v) {
				matched = true
				break
			}
		}
		if !matched {
			return false
		}
	}
	return true
}
```
