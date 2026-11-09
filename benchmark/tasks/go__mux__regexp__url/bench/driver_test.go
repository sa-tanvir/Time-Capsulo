package mux

// Time Capsulo bench driver for (*routeRegexp).url. Copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
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
			Tpl    string      `json:"tpl"`
			Typ    int         `json:"typ"`
			Strict bool        `json:"strict"`
			Vals   [][2]string `json:"vals"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	rrs := make([]*routeRegexp, n)
	vals := make([]map[string]string, n)
	for i, c := range doc.Cases {
		rr, err := newRouteRegexp(c.Tpl, regexpType(c.Typ), routeRegexpOptions{strictSlash: c.Strict})
		if err != nil {
			t.Fatalf("case %d: %v", i, err)
		}
		rrs[i] = rr
		vals[i] = make(map[string]string, len(c.Vals))
		for _, kv := range c.Vals {
			vals[i][kv[0]] = kv[1]
		}
	}
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			s, err := rrs[i].url(vals[i])
			if err != nil {
				fmt.Fprintf(h, "err %q\n", err.Error())
			} else {
				fmt.Fprintf(h, "ok %q\n", s)
			}
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			s, err := rrs[i].url(vals[i])
			sink += len(s)
			if err != nil {
				sink++
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el)
}
