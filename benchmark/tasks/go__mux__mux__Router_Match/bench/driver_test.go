package mux

// Time Capsulo bench driver for (*Router).Match. Copied into the package as zz_tcbench_test.go.
// Routers and requests are built outside the timed region; every call gets a fresh RouteMatch.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
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

func tcMw(name string) MiddlewareFunc {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("<" + name + ">"))
			next.ServeHTTP(w, r)
		})
	}
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
			Routes []tcRouteSpec `json:"routes"`
			Mw     int           `json:"mw"`
			NF     bool          `json:"nf"`
			MNA    bool          `json:"mna"`
			Reqs   []tcReqSpec   `json:"reqs"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	var routers []*Router
	var reqs []*http.Request
	for i, c := range doc.Cases {
		rt := NewRouter()
		for j, s := range c.Routes {
			r := tcBuildRoute(rt.NewRoute(), s, fmt.Sprintf("r%d", j))
			if r.err != nil {
				t.Fatalf("case %d route %d: %v", i, j, r.err)
			}
		}
		for k := 0; k < c.Mw; k++ {
			rt.Use(tcMw(fmt.Sprintf("mw%d", k)))
		}
		if c.NF {
			rt.NotFoundHandler = tcNamedHandler("router-404")
		}
		if c.MNA {
			rt.MethodNotAllowedHandler = tcNamedHandler("router-405")
		}
		for _, q := range c.Reqs {
			routers = append(routers, rt)
			reqs = append(reqs, tcBuildRequest(q))
		}
	}
	n := len(reqs)
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			var m RouteMatch
			ok := routers[i].Match(reqs[i], &m)
			tcDescribe(h, ok, &m, reqs[i])
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			var m RouteMatch
			if routers[i].Match(reqs[i], &m) {
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
	SubMw     int           `json:"subMw"`
	SubNF     bool          `json:"subNF"`
	SubMNA    bool          `json:"subMNA"`
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
		for k := 0; k < s.SubMw; k++ {
			sr.Use(tcMw(fmt.Sprintf("%s-mw%d", name, k)))
		}
		if s.SubNF {
			sr.NotFoundHandler = tcNamedHandler(name + "-404")
		}
		if s.SubMNA {
			sr.MethodNotAllowedHandler = tcNamedHandler(name + "-405")
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

