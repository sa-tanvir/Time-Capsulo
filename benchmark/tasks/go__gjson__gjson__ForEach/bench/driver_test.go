package gjson

// Time Capsulo bench driver for ForEach. It is copied into the package as zz_tcbench_test.go.
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

func tcFmtResult(r Result) string {
	return fmt.Sprintf("{%d %q %q %s %d}", r.Type, r.Raw, r.Str, strconv.FormatFloat(r.Num, 'g', -1, 64), r.Index)
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
	ncases := len(doc.Cases)
	res := make([]Result, ncases)
	stops := make([]int, ncases)
	for k, c := range doc.Cases {
		res[k] = Result{Type: Type(int(c[0].(float64))), Raw: c[1].(string), Str: c[2].(string), Num: c[3].(float64)}
		stops[k] = int(c[4].(float64))
	}
	if mode == "check" {
		h := sha256.New()
		for k := range res {
			calls := 0
			res[k].ForEach(func(key, value Result) bool {
				calls++
				fmt.Fprintf(h, "%s=%s;", tcFmtResult(key), tcFmtResult(value))
				return calls != stops[k]
			})
			fmt.Fprintf(h, "#%d\n", calls)
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", ncases, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for k := range res {
			calls, stop := 0, stops[k]
			res[k].ForEach(func(key, value Result) bool {
				calls++
				sink += len(key.Str) + len(value.Raw)
				return calls != stop
			})
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", ncases, repeat, el)
}
