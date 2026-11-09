func PluralWord(quantity int, singular, plural string) string {
	if quantity == 1 {
		return singular
	}
	if plural != "" {
		return plural
	}
	if plural = specialPlurals[singular]; plural != "" {
		return plural
	}

	// We need to guess what the English plural might be.  Keep this
	// function simple!  It doesn't need to know about every possiblity;
	// only regular rules and the most common special cases.
	//
	// Reference: http://en.wikipedia.org/wiki/English_plural

	for _, ending := range sibilantEndings {
		if strings.HasSuffix(singular, ending) {
			return singular + "es"
		}
	}
	l := len(singular)
	if l >= 2 && singular[l-1] == 'o' && !isVowel[singular[l-2]] {
		return singular + "es"
	}
	if l >= 2 && singular[l-1] == 'y' && !isVowel[singular[l-2]] {
		return singular[:l-1] + "ies"
	}

	return singular + "s"
}
