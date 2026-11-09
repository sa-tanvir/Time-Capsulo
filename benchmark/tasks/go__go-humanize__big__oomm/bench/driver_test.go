package humanize

// Time Capsulo bench driver for oomm. It is copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).
// oomm overwrites n, so every call gets a fresh copy, built outside the timed region.

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
		Cases [][3]json.RawMessage `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	k := len(doc.Cases)
	orig := make([]*big.Int, k)
	bases := make([]*big.Int, k)
	caps := make([]int, k)
	for i, c := range doc.Cases {
		var s string
		var b int64
		if err := json.Unmarshal(c[0], &s); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(c[1], &b); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(c[2], &caps[i]); err != nil {
			t.Fatal(err)
		}
		v, ok := new(big.Int).SetString(s, 10)
		if !ok {
			t.Fatalf("bad value %q", s)
		}
		orig[i], bases[i] = v, big.NewInt(b)
	}
	work := make([]*big.Int, k)
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
		for i := range work {
			f, m := oomm(work[i], bases[i], caps[i])
			fmt.Fprintf(h, "%s %d\n", strconv.FormatFloat(f, 'g', -1, 64), m)
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", k, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0.0
	var el time.Duration
	for r := 0; r < repeat; r++ {
		reset() // untimed: restore inputs overwritten by the previous pass
		t0 := time.Now()
		for i := range work {
			f, m := oomm(work[i], bases[i], caps[i])
			sink += f + float64(m)
		}
		el += time.Since(t0)
	}
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", k, repeat, el.Seconds())
}
