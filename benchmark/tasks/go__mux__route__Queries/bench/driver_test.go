package mux

// Time Capsulo bench driver for (*Route).Queries. Copied into the package as zz_tcbench_test.go.
// Queries mutates its receiver, so fresh copies of the base routes are built outside the timed region.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"testing"
	"time"
)

func tcFresh(bases []*Route) []*Route {
	out := make([]*Route, len(bases))
	for i, b := range bases {
		out[i] = &Route{err: b.err, namedRoutes: b.namedRoutes, routeConf: copyRouteConf(b.routeConf)}
	}
	return out
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
			Host   string   `json:"host"`
			Path   string   `json:"path"`
			PreErr bool     `json:"preerr"`
			Pairs  []string `json:"pairs"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	bases := make([]*Route, n)
	pairs := make([][]string, n)
	for i, c := range doc.Cases {
		r := &Route{namedRoutes: map[string]*Route{}}
		if c.Host != "" {
			r.Host(c.Host)
		}
		if c.Path != "" {
			r.Path(c.Path)
		}
		if c.PreErr {
			r.err = errors.New("pre-existing route error")
		}
		bases[i] = r
		pairs[i] = c.Pairs
	}
	if mode == "check" {
		h := sha256.New()
		routes := tcFresh(bases)
		for i := 0; i < n; i++ {
			ret := routes[i].Queries(pairs[i]...)
			r := routes[i]
			fmt.Fprintf(h, "ret_nil=%v same=%v err=%v matchers=%d\n", ret == nil, ret == r, r.err, len(r.matchers))
			for _, q := range r.regexp.queries {
				fmt.Fprintf(h, "  q %q %q %q %d\n", q.template, q.regexp.String(), q.varsN, q.regexpType)
			}
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	var el time.Duration
	for r := 0; r < repeat; r++ {
		routes := tcFresh(bases) // untimed: Queries mutates the route
		t0 := time.Now()
		for i := 0; i < n; i++ {
			if routes[i].Queries(pairs[i]...) != nil {
				sink++
			}
		}
		el += time.Since(t0)
	}
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el.Seconds())
}
