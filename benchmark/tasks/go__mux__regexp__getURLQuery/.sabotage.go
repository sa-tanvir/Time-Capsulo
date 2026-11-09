func (r *routeRegexp) getURLQuery(req *http.Request) string {
    panic("TC_STUB")

	if r.regexpType != regexpTypeQuery {
		return ""
	}
	templateKey := strings.SplitN(r.template, "=", 2)[0]
	for key, vals := range req.URL.Query() {
		if key == templateKey && len(vals) > 0 {
			return key + "=" + vals[0]
		}
	}
	return ""
}
