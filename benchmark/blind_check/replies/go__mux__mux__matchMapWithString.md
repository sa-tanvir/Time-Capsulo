```go
func matchMapWithString(toCheck map[string]string, toMatch map[string][]string, canonicalKey bool) bool {
	for k, v := range toCheck {
		if canonicalKey {
			k = http.CanonicalHeaderKey(k)
		}
		values := toMatch[k]
		if values == nil {
			return false
		}
		if v == "" {
			continue
		}
		found := false
		for _, value := range values {
			if value == v {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}
	return true
}
```
