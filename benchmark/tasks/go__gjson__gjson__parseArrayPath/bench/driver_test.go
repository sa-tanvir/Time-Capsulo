package gjson

// Time Capsulo bench driver for parseArrayPath. It is copied into the package as zz_tcbench_test.go.
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

func tcFmtArrayPath(r arrayPathResult) string {
	return fmt.Sprintf("part=%q path=%q pipe=%q piped=%v more=%v alogok=%v arrch=%v alogkey=%q q.on=%v q.path=%q q.op=%q q.value=%q q.all=%v",
		r.part, r.path, r.pipe, r.piped, r.more, r.alogok, r.arrch, r.alogkey,
		r.query.on, r.query.path, r.query.op, r.query.value, r.query.all)
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
			fmt.Fprintln(h, tcFmtArrayPath(parseArrayPath(c)))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", ncases, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cases {
			r := parseArrayPath(c)
			sink += len(r.part) + len(r.path) + len(r.query.value)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", ncases, repeat, el)
}
