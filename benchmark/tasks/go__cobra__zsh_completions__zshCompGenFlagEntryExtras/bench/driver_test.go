package cobra

// Time Capsulo bench driver for zshCompGenFlagEntryExtras. Copied into the package as zz_tcbench_test.go.
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

	"github.com/spf13/pflag"
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
		Cases [][2]json.RawMessage `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	fs := make([]*pflag.Flag, len(doc.Cases))
	for k, c := range doc.Cases {
		f := &pflag.Flag{Name: "f" + strconv.Itoa(k)}
		if err := json.Unmarshal(c[0], &f.NoOptDefVal); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(c[1], &f.Annotations); err != nil {
			t.Fatal(err)
		}
		fs[k] = f
	}
	if mode == "check" {
		h := sha256.New()
		for _, f := range fs {
			fmt.Fprintf(h, "%q\n", zshCompGenFlagEntryExtras(f))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(fs), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, f := range fs {
			sink += len(zshCompGenFlagEntryExtras(f))
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(fs), repeat, el)
}
