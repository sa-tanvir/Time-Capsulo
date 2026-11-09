```go
func PluralWord(quantity int, singular, plural string) string {
	if quantity == 1 {
		return singular
	}
	if plural != "" {
		return plural
	}
	if p, ok := specialPlurals[singular]; ok {
		return p
	}
	for _, ending := range sibilantEndings {
		if strings.HasSuffix(singular, ending) {
			return singular + "es"
		}
	}
	n := len(singular)
	if n >= 2 {
		last := singular[n-1]
		prev := singular[n-2]
		if last == 'o' && !isVowel[prev] {
			return singular + "es"
		}
		if last == 'y' && !isVowel[prev] {
			return singular[:n-1] + "ies"
		}
	}
	return singular + "s"
}
```
