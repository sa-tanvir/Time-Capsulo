```go
func (v routeRegexpGroup) setMatch(req *http.Request, m *RouteMatch, r *Route) {
	// Host variables.
	if v.host != nil {
		host := getHost(req)
		if matches := v.host.regexp.FindStringSubmatchIndex(host); matches != nil {
			extractVars(host, matches, v.host.varsN, m.Vars)
		}
	}

	// Path variables and strict-slash redirect.
	path := req.URL.Path
	if r.useEncodedPath {
		path = req.URL.EscapedPath()
	}
	if v.path != nil {
		if matches := v.path.regexp.FindStringSubmatchIndex(path); matches != nil {
			extractVars(path, matches, v.path.varsN, m.Vars)
			if v.path.options.strictSlash {
				p1 := strings.HasSuffix(path, "/")
				p2 := strings.HasSuffix(v.path.template, "/")
				if p1 != p2 {
					if u, err := url.Parse(req.URL.String()); err == nil {
						if p1 {
							u.Path = u.Path[:len(u.Path)-1]
						} else {
							u.Path += "/"
						}
						m.Handler = http.RedirectHandler(u.String(), http.StatusMovedPermanently)
					}
				}
			}
		}
	}

	// Query variables.
	for _, q := range v.queries {
		queryURL := q.getURLQuery(req)
		if matches := q.regexp.FindStringSubmatchIndex(queryURL); matches != nil {
			extractVars(queryURL, matches, q.varsN, m.Vars)
		}
	}
}
```
