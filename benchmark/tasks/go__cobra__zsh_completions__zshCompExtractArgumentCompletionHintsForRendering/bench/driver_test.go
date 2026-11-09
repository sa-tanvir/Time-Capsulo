package cobra

// Time Capsulo bench driver for zshCompExtractArgumentCompletionHintsForRendering.
// Copied into the package as zz_tcbench_test.go.
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
		Cases [][2]json.RawMessage `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	cmds := make([]*Command, len(doc.Cases))
	for k, c := range doc.Cases {
		cmd := &Command{Use: "c" + strconv.Itoa(k), Run: func(*Command, []string) {}}
		var ann *string
		if err := json.Unmarshal(c[0], &ann); err != nil {
			t.Fatal(err)
		}
		if ann != nil {
			cmd.Annotations = map[string]string{"other": "x", zshCompArgumentAnnotation: *ann}
		}
		if err := json.Unmarshal(c[1], &cmd.ValidArgs); err != nil {
			t.Fatal(err)
		}
		cmds[k] = cmd
	}
	if mode == "check" {
		h := sha256.New()
		for _, c := range cmds {
			res, err := zshCompExtractArgumentCompletionHintsForRendering(c)
			if err != nil {
				fmt.Fprintf(h, "ERR\n")
			} else {
				fmt.Fprintf(h, "%d %q\n", len(res), res)
			}
			fmt.Fprintf(h, "%q %q\n", c.Annotations[zshCompArgumentAnnotation], c.ValidArgs)
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cmds), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cmds {
			res, _ := zshCompExtractArgumentCompletionHintsForRendering(c)
			sink += len(res)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cmds), repeat, el)
}
