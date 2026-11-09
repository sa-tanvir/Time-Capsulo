package humanize

// Time Capsulo bench driver for BigComma. It is copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).
// BigComma may modify its argument, so every call gets a fresh copy, built outside the timed region.

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/big"
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
	orig := make([]*big.Int, len(doc.Values))
	for i, s := range doc.Values {
		v, ok := new(big.Int).SetString(s, 10)
		if !ok {
			t.Fatalf("bad value %q", s)
		}
		orig[i] = v
	}
	work := make([]*big.Int, len(orig))
	for i := range work {
		work[i] = new(big.Int)
	}
	reset := func() {
		for i, v := range orig {
			work[i].Set(v)
		}
	}
	if mode == "check" {
		reset()
		h := sha256.New()
		for _, v := range work {
			fmt.Fprintf(h, "%q\n", BigComma(v))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(orig), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	var el time.Duration
	for r := 0; r < repeat; r++ {
		reset() // untimed: restore inputs that the previous pass may have modified
		t0 := time.Now()
		for _, v := range work {
			sink += len(BigComma(v))
		}
		el += time.Since(t0)
	}
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(orig), repeat, el.Seconds())
}
