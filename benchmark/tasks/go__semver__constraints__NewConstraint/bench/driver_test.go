package semver

// Time Capsulo bench driver for NewConstraint. It is copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"hash"
	"io/ioutil"
	"os"
	"strconv"
	"testing"
	"time"
)

func tcDumpConstraints(h hash.Hash, cs *Constraints, err error) {
	if err != nil {
		fmt.Fprintf(h, "E %q\n", err.Error())
		return
	}
	if cs == nil {
		fmt.Fprintf(h, "nil\n")
		return
	}
	fmt.Fprintf(h, "G %d\n", len(cs.constraints))
	for _, g := range cs.constraints {
		fmt.Fprintf(h, " A %d\n", len(g))
		for _, c := range g {
			if c == nil || c.con == nil {
				fmt.Fprintf(h, "  nil\n")
				continue
			}
			v := c.con
			fmt.Fprintf(h, "  %q %q %d %d %d %q %q %q %t %t %t\n", c.origfunc, c.orig,
				v.major, v.minor, v.patch, v.pre, v.metadata, v.original, c.dirty, c.minorDirty, c.patchDirty)
		}
	}
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
		Inner int      `json:"inner"`
		Cases []string `json:"cases"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}
	cs := doc.Cases
	if mode == "check" {
		h := sha256.New()
		for _, s := range cs {
			c, err := NewConstraint(s)
			tcDumpConstraints(h, c, err)
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cs), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for k := 0; k < doc.Inner; k++ {
			for i := range cs {
				if c, err := NewConstraint(cs[i]); err == nil {
					sink += len(c.constraints)
				} else {
					sink--
				}
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cs)*doc.Inner, repeat, el)
}
