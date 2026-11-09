package mux

// Time Capsulo bench driver for (*Route).URL. Copied into the package as zz_tcbench_test.go.
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
	"strings"
	"testing"
	"time"
)

func tcBuildVars(m map[string]string) map[string]string {
	// deterministic BuildVarsFunc: upper-cases nothing, rewrites one known key and adds an unused one
	if v, ok := m["p0"]; ok {
		m["p0"] = strings.ToLower(v)
	}
	m["bvf-extra"] = "1"
	return m
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
			Host    string   `json:"host"`
			Path    string   `json:"path"`
			Prefix  bool     `json:"prefix"`
			Queries []string `json:"queries"`
			Schemes []string `json:"schemes"`
			Bvf     bool     `json:"bvf"`
			PreErr  bool     `json:"preerr"`
			Pairs   []string `json:"pairs"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	routes := make([]*Route, n)
	pairs := make([][]string, n)
	for i, c := range doc.Cases {
		r := NewRouter().NewRoute()
		if len(c.Schemes) > 0 {
			r.Schemes(c.Schemes...)
		}
		if c.Host != "" {
			r.Host(c.Host)
		}
		if c.Path != "" {
			if c.Prefix {
				r.PathPrefix(c.Path)
			} else {
				r.Path(c.Path)
			}
		}
		if len(c.Queries) > 0 {
			r.Queries(c.Queries...)
		}
		if c.Bvf {
			r.BuildVarsFunc(tcBuildVars)
		}
		if r.err != nil {
			t.Fatalf("case %d: %v", i, r.err)
		}
		if c.PreErr {
			r.err = errors.New("pre-existing route error")
		}
		routes[i] = r
		pairs[i] = c.Pairs
	}
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			u, err := routes[i].URL(pairs[i]...)
			if err != nil {
				fmt.Fprintf(h, "err nil=%v %q\n", u == nil, err.Error())
			} else {
				fmt.Fprintf(h, "ok %q %q %q %q %q %q\n", u.String(), u.Scheme, u.Host, u.Path, u.RawQuery, u.Opaque)
			}
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			u, err := routes[i].URL(pairs[i]...)
			if err == nil {
				sink += len(u.Path) + len(u.RawQuery)
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el)
}
