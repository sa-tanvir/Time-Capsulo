```go
func tostr(json string) (raw string, str string) {
	// expects that the lead character is a '"'
	escaped := false
	end := len(json)
	for i := 1; i < len(json); i++ {
		if json[i] == '\\' {
			escaped = true
			i++
			continue
		}
		if json[i] == '"' {
			end = i
			break
		}
	}
	if !escaped {
		if end < len(json) {
			return json[:end+1], json[1:end]
		}
		return json, json[1:]
	}
	str = unescape(json[1:end])
	if end+1 < len(json) {
		return json[:end+1], str
	}
	return json[:end], str
}
```
