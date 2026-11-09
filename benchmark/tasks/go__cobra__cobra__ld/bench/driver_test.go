package cobra

// Time Capsulo bench driver for ld. Copied into the package as zz_tcbench_test.go.
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
		Cases [][3]interface{} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	type tc struct {
		s, t string
		ic   bool
	}
	cs := make([]tc, len(doc.Cases))
	for i, c := range doc.Cases {
		cs[i] = tc{c[0].(string), c[1].(string), c[2].(bool)}
	}
	if mode == "check" {
		h := sha256.New()
		for _, c := range cs {
			fmt.Fprintf(h, "%d\n", ld(c.s, c.t, c.ic))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cs), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cs {
			sink += ld(c.s, c.t, c.ic)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cs), repeat, el)
}
