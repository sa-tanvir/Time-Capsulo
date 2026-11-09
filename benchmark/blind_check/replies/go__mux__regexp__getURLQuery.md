```go
func (r *routeRegexp) getURLQuery(req *http.Request) string {
	if r.regexpType != regexpTypeQuery {
		return ""
	}
	key := r.template
	if i := strings.IndexByte(key, '='); i >= 0 {
		key = key[:i]
	}
	values := req.URL.Query()[key]
	if len(values) == 0 {
		return ""
	}
	return key + "=" + values[0]
}
```
