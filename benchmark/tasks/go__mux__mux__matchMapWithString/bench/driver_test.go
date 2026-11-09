package mux

// Time Capsulo bench driver for matchMapWithString. Copied into the package as zz_tcbench_test.go.
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

type tcCase struct {
	Canon bool              `json:"canon"`
	Check [][2]string       `json:"check"`
	Match []json.RawMessage `json:"match"`
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
		Cases []tcCase `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	n := len(doc.Cases)
	checks := make([]map[string]string, n)
	matches := make([]map[string][]string, n)
	canon := make([]bool, n)
	for i, c := range doc.Cases {
		checks[i] = make(map[string]string, len(c.Check))
		for _, kv := range c.Check {
			checks[i][kv[0]] = kv[1]
		}
		matches[i] = make(map[string][]string, len(c.Match))
		for _, m := range c.Match {
			var pair []json.RawMessage
			if err := json.Unmarshal(m, &pair); err != nil {
				t.Fatal(err)
			}
			var k string
			var vs []string
			json.Unmarshal(pair[0], &k)
			json.Unmarshal(pair[1], &vs)
			if vs == nil {
				vs = []string{}
			}
			matches[i][k] = vs
		}
		canon[i] = c.Canon
	}
	if mode == "check" {
		h := sha256.New()
		for i := 0; i < n; i++ {
			fmt.Fprintf(h, "%v\n", matchMapWithString(checks[i], matches[i], canon[i]))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", n, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for i := 0; i < n; i++ {
			if matchMapWithString(checks[i], matches[i], canon[i]) {
				sink++
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", n, repeat, el)
}
