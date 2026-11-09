package humanize

// Time Capsulo bench driver for Comma. It is copied into the package as zz_tcbench_test.go.
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
		Inner  int      `json:"inner"`
		Values []string `json:"values"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	vals := make([]int64, len(doc.Values))
	for i, s := range doc.Values {
		if vals[i], err = strconv.ParseInt(s, 10, 64); err != nil {
			t.Fatal(err)
		}
	}
	if mode == "check" {
		h := sha256.New()
		for _, v := range vals {
			fmt.Fprintf(h, "%q\n", Comma(v))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(vals), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for k := 0; k < doc.Inner; k++ {
			for _, v := range vals {
				sink += len(Comma(v))
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(vals)*doc.Inner, repeat, el)
}
