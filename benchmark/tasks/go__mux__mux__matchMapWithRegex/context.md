# Context for the function to implement

- **Language:** go
- **File:** `mux.go`

## Imports / includes available in this file

```
import "errors"
import "fmt"
import "net/http"
import "path"
import "regexp"
```

## Other functions defined in the same file (signatures only; you may call them)

```
(r*Router)BuildVarsFunc f BuildVarsFunc
(r*Router)Get name string
(r*Router)GetRoute name string
(r*Router)Handle path string , handler http . Handler
(r*Router)HandleFunc path string , f func http . ResponseWriter , * http . Request
(r*Router)Headers pairs ... string
(r*Router)Host tpl string
(r*Router)Match req * http . Request , match * RouteMatch
(r*Router)MatcherFunc f MatcherFunc
(r*Router)Methods methods ... string
(r*Router)NewRoute
(r*Router)Path tpl string
(r*Router)PathPrefix tpl string
(r*Router)Queries pairs ... string
(r*Router)Schemes schemes ... string
(r*Router)ServeHTTP w http . ResponseWriter , req * http . Request
(r*Router)SkipClean value bool
(r*Router)StrictSlash value bool
(r*Router)UseEncodedPath
(r*Router)Walk walkFn WalkFunc
CurrentRoute r * http . Request
NewRouter
Vars r * http . Request
checkPairs pairs ... string
cleanPath p string
copyRouteConf r routeConf
copyRouteRegexp r * routeRegexp
mapFromPairsToRegex pairs ... string
mapFromPairsToString pairs ... string
matchInArray arr [ ] string , value string
matchMapWithString toCheck map [ string ] string , toMatch map [ string ] [ ] string , canonicalKey bool
methodNotAllowed w http . ResponseWriter , r * http . Request
methodNotAllowedHandler
setCurrentRoute r * http . Request , val interface { }
setVars r * http . Request , val interface { }
uniqueVars s1 , s2 [ ] string
```

## Notes

`http.CanonicalHeaderKey` (package `net/http`, imported in this file) returns
the canonical MIME header form of a key. The matcher type that uses this
function is:

```go
// headerRegexMatcher matches the request against the route given a regex for the header
type headerRegexMatcher map[string]*regexp.Regexp

func (m headerRegexMatcher) Match(r *http.Request, match *RouteMatch) bool {
	return matchMapWithRegex(m, r.Header, true)
}
```
