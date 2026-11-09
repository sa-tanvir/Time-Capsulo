package gjson

// Time Capsulo bench driver for parseSubSelectors. It is copied into the package as zz_tcbench_test.go.
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
		Cases []string `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	cases := doc.Cases
	ncases := len(cases)
	if mode == "check" {
		h := sha256.New()
		for _, c := range cases {
			sels, out, ok := parseSubSelectors(c)
			fmt.Fprintf(h, "%v|%q", ok, out)
			if ok {
				fmt.Fprintf(h, "|%d", len(sels))
				for _, s := range sels {
					fmt.Fprintf(h, "|%q:%q", s.name, s.path)
				}
			}
			fmt.Fprintln(h)
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", ncases, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cases {
			sels, out, _ := parseSubSelectors(c)
			sink += len(sels) + len(out)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", ncases, repeat, el)
}
