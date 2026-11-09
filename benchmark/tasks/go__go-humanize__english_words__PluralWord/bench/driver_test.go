package english

// Time Capsulo bench driver for PluralWord. It is copied into the package as zz_tcbench_test.go.
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
	q        int
	singular string
	plural   string
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
		Cases [][]interface{} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	cases := make([]tcCase, len(doc.Cases))
	for i, c := range doc.Cases {
		cases[i] = tcCase{int(c[0].(float64)), c[1].(string), c[2].(string)}
	}
	if mode == "check" {
		h := sha256.New()
		for _, c := range cases {
			fmt.Fprintf(h, "%q\n", PluralWord(c.q, c.singular, c.plural))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cases), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cases {
			sink += len(PluralWord(c.q, c.singular, c.plural))
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cases), repeat, el)
}
