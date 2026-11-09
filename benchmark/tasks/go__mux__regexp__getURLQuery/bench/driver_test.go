package mux

// Time Capsulo bench driver for (*routeRegexp).getURLQuery. Copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"testing"
	"time"
)

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
			Tpl string `json:"tpl"`
			Typ int    `json:"typ"`
			Q   string `json:"q"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	rrs := make([]*routeRegexp, n)
	reqs := make([]*http.Request, n)
	for i, c := range doc.Cases {
		rr, err := newRouteRegexp(c.Tpl, regexpType(c.Typ), routeRegexpOptions{})
		if err != nil {
			t.Fatalf("case %d: %v", i, err)
		}
		rrs[i] = rr
		reqs[i] = &http.Request{Method: "GET", URL: &url.URL{Scheme: "http", Host: "localhost", Path: "/", RawQuery: c.Q}, Host: "localhost", Header: http.Header{}}
	}
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			fmt.Fprintf(h, "%q\n", rrs[i].getURLQuery(reqs[i]))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			sink += len(rrs[i].getURLQuery(reqs[i]))
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el)
}
