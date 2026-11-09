package cobra

// Time Capsulo bench driver for zshCompRenderZshCompArgHint. Copied into the package as zz_tcbench_test.go.
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
		Cases [][3]json.RawMessage `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	type tc struct {
		i int
		z zshCompArgHint
	}
	cs := make([]tc, len(doc.Cases))
	for k, c := range doc.Cases {
		if err := json.Unmarshal(c[0], &cs[k].i); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(c[1], &cs[k].z.Tipe); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(c[2], &cs[k].z.Options); err != nil {
			t.Fatal(err)
		}
	}
	if mode == "check" {
		h := sha256.New()
		for _, c := range cs {
			s, err := zshCompRenderZshCompArgHint(c.i, c.z)
			if err != nil {
				fmt.Fprintf(h, "ERR\n")
			} else {
				fmt.Fprintf(h, "%q\n", s)
			}
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cs), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cs {
			s, _ := zshCompRenderZshCompArgHint(c.i, c.z)
			sink += len(s)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cs), repeat, el)
}
