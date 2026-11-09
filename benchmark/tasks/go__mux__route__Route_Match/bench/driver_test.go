package mux

// Time Capsulo bench driver for (*Route).Match. Copied into the package as zz_tcbench_test.go.
// Routes and requests are built outside the timed region; every call gets a fresh RouteMatch
// (optionally pre-populated as a router would leave it after earlier routes).
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"sort"
	"strconv"
	"strings"
	"testing"
	"time"
)

var tcPrevRoute = &Route{name: "prev-route"}
var tcPrevHandler = tcNamedHandler("prev-handler")

func tcPre(pre int, vars map[string]string) RouteMatch {
	switch pre {
	case 1:
		return RouteMatch{MatchErr: ErrMethodMismatch, Handler: tcPrevHandler}
	case 2:
		return RouteMatch{MatchErr: ErrNotFound}
	case 3:
		vars["pre"] = "x"
		return RouteMatch{Route: tcPrevRoute, Handler: tcPrevHandler, Vars: vars}
	}
	return RouteMatch{}
}

func TestTCBench(t *testing.T) {
	mode := os.Getenv("TC_MODE")
	if mode == "" {
		t.Skip("TC_MODE not set")
	}
	repeat, _ := strconv.Atoi(os.Getenv("TC_REPEAT"))
	if repeat < 1 {
		repeat = 1
	}
	raw, err := ioutil.ReadFile(os.Getenv("TC_TASK") + "/bench/workload_" + os.Getenv("TC_SIZE") + ".json")
	if err != nil {
		t.Fatal(err)
	}
	var doc struct {
		Cases []struct {
			Route tcRouteSpec `json:"route"`
			Req   tcReqSpec   `json:"req"`
			Pre   int         `json:"pre"`
			Err   bool        `json:"err"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	routes := make([]*Route, n)
	reqs := make([]*http.Request, n)
	pres := make([]int, n)
	maps := make([]map[string]string, n)
	for i, c := range doc.Cases {
		routes[i] = tcBuildRoute(NewRouter().NewRoute(), c.Route, fmt.Sprintf("r%d", i))
		if routes[i].err != nil {
			t.Fatalf("case %d: %v", i, routes[i].err)
		}
		if c.Err {
			routes[i].err = errors.New("route build error")
		}
		reqs[i] = tcBuildRequest(c.Req)
		pres[i] = c.Pre
		maps[i] = map[string]string{}
	}
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			m := tcPre(pres[i], map[string]string{})
			ok := routes[i].Match(reqs[i], &m)
			tcDescribe(h, ok, &m, reqs[i])
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			m := tcPre(pres[i], maps[i])
			if routes[i].Match(reqs[i], &m) {
				sink += len(m.Vars)
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el)
}

// ---- shared helpers: build routes/requests from the workload, describe results ----

type tcRouteSpec struct {
	Host      string        `json:"host"`
	Path      string        `json:"path"`
	Prefix    bool          `json:"prefix"`
	Strict    bool          `json:"strict"`
	Encoded   bool          `json:"encoded"`
	BuildOnly bool          `json:"buildOnly"`
	Methods   []string      `json:"methods"`
	Schemes   []string      `json:"schemes"`
	Headers   []string      `json:"headers"`
	HeadersRe []string      `json:"headersRe"`
	Queries   []string      `json:"queries"`
	Sub       []tcRouteSpec `json:"sub"`
}

type tcReqSpec struct {
	Method   string   `json:"method"`
	URL      string   `json:"url"`
	Host     string   `json:"host"`
	Relative bool     `json:"relative"`
	Headers  []string `json:"headers"`
}

func tcNamedHandler(name string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.Write([]byte("[" + name + "]")) })
}

func tcBuildRoute(rt *Route, s tcRouteSpec, name string) *Route {
	if s.Strict {
		rt.strictSlash = true
	}
	if s.Encoded {
		rt.useEncodedPath = true
	}
	if len(s.Schemes) > 0 {
		rt.Schemes(append([]string(nil), s.Schemes...)...)
	}
	if s.Host != "" {
		rt.Host(s.Host)
	}
	if s.Path != "" {
		if s.Prefix {
			rt.PathPrefix(s.Path)
		} else {
			rt.Path(s.Path)
		}
	}
	if len(s.Methods) > 0 {
		rt.Methods(append([]string(nil), s.Methods...)...)
	}
	if len(s.Headers) > 0 {
		rt.Headers(s.Headers...)
	}
	if len(s.HeadersRe) > 0 {
		rt.HeadersRegexp(s.HeadersRe...)
	}
	if len(s.Queries) > 0 {
		rt.Queries(s.Queries...)
	}
	rt.Name(name)
	rt.Handler(tcNamedHandler(name))
	if len(s.Sub) > 0 {
		sr := rt.Subrouter()
		for j, c := range s.Sub {
			tcBuildRoute(sr.NewRoute(), c, fmt.Sprintf("%s/%d", name, j))
		}
	}
	if s.BuildOnly {
		rt.BuildOnly()
	}
	return rt
}

func tcBuildRequest(s tcReqSpec) *http.Request {
	req, err := http.NewRequest(s.Method, s.URL, nil)
	if err != nil {
		panic(err)
	}
	if s.Relative {
		req.Host = s.Host
	}
	for i := 0; i+1 < len(s.Headers); i += 2 {
		req.Header.Add(s.Headers[i], s.Headers[i+1])
	}
	return req
}

type tcWriter struct {
	h    http.Header
	code int
	body []byte
}

func (w *tcWriter) Header() http.Header         { return w.h }
func (w *tcWriter) Write(b []byte) (int, error) { w.body = append(w.body, b...); return len(b), nil }
func (w *tcWriter) WriteHeader(c int)           { w.code = c }

func tcVars(m map[string]string) string {
	if m == nil {
		return "nil"
	}
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	var b strings.Builder
	for _, k := range keys {
		fmt.Fprintf(&b, "%q=%q;", k, m[k])
	}
	return b.String()
}

func tcDescribe(h io.Writer, ok bool, m *RouteMatch, req *http.Request) {
	rn := "nil"
	if m.Route != nil {
		rn = m.Route.GetName()
	}
	fmt.Fprintf(h, "ok=%v err=%v route=%q vars=%s", ok, m.MatchErr, rn, tcVars(m.Vars))
	if m.Handler == nil {
		fmt.Fprintf(h, " handler=nil\n")
		return
	}
	w := &tcWriter{h: http.Header{}}
	m.Handler.ServeHTTP(w, req)
	fmt.Fprintf(h, " code=%d loc=%q body=%q\n", w.code, w.h.Get("Location"), w.body)
}
