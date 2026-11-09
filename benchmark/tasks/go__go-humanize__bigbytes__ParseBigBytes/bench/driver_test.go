package humanize

// Time Capsulo bench driver for ParseBigBytes. It is copied into the package as zz_tcbench_test.go.
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
		Values []string `json:"values"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	vals := doc.Values
	if mode == "check" {
		h := sha256.New()
		for _, s := range vals {
			v, err := ParseBigBytes(s)
			if err != nil {
				fmt.Fprintf(h, "ERR %v\n", v == nil) // error kind only; messages may differ
			} else {
				fmt.Fprintf(h, "%s\n", v.String())
			}
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(vals), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	nerr := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, s := range vals {
			v, err := ParseBigBytes(s)
			if err != nil {
				nerr++
			} else {
				sink += v.BitLen()
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink, nerr)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(vals), repeat, el)
}
