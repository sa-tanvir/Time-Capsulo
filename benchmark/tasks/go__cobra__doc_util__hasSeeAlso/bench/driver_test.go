package doc

// Time Capsulo bench driver for hasSeeAlso. Copied into the package as zz_tcbench_test.go.
// Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK (task dir).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/spf13/cobra"
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
	var wl struct {
		Cases []struct {
			T  *tcNode `json:"t"`
			P  []int   `json:"p"`
			IH bool    `json:"ih"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &wl); err != nil {
		t.Fatal(err)
	}
	cmds := make([]*cobra.Command, len(wl.Cases))
	for k, c := range wl.Cases {
		root := tcBuild(c.T)
		if c.IH {
			root.InitDefaultHelpCmd()
		}
		cmds[k] = tcFollow(root, c.P)
	}
	if mode == "check" {
		h := sha256.New()
		for _, c := range cmds {
			fmt.Fprintf(h, "%v\n", hasSeeAlso(c))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", len(cmds), hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for _, c := range cmds {
			if hasSeeAlso(c) {
				sink++
			}
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", len(cmds), repeat, el)
}

// ---- command-tree builder (shared by the cobra Time Capsulo drivers) ----

type tcNode struct {
	U  string      `json:"u"`
	S  string      `json:"s"`
	L  string      `json:"l"`
	E  string      `json:"e"`
	R  bool        `json:"r"`
	H  bool        `json:"h"`
	D  string      `json:"d"`
	A  []string    `json:"a"`
	VA []string    `json:"va"`
	AA []string    `json:"aa"`
	NT bool        `json:"nt"`
	F  [][]string  `json:"f"` // kind, name, shorthand, default, usage, "p"|"l", "hidden"|"", deprecated msg, annotation key, annotation values...
	C  []*tcNode   `json:"c"`
}

func tcBuild(n *tcNode) *cobra.Command {
	c := &cobra.Command{Use: n.U, Short: n.S, Long: n.L, Example: n.E, Hidden: n.H, Deprecated: n.D,
		Aliases: n.A, ValidArgs: n.VA, ArgAliases: n.AA, DisableAutoGenTag: n.NT}
	if n.R {
		c.Run = func(*cobra.Command, []string) {}
	}
	for _, f := range n.F {
		fs := c.Flags()
		if f[5] == "p" {
			fs = c.PersistentFlags()
		}
		switch f[0] {
		case "string":
			fs.StringP(f[1], f[2], f[3], f[4])
		case "bool":
			fs.BoolP(f[1], f[2], f[3] == "true", f[4])
		case "int":
			v, _ := strconv.Atoi(f[3])
			fs.IntP(f[1], f[2], v, f[4])
		case "slice":
			var v []string
			if f[3] != "" {
				v = strings.Split(f[3], ",")
			}
			fs.StringSliceP(f[1], f[2], v, f[4])
		}
		if f[6] == "hidden" {
			fs.MarkHidden(f[1])
		}
		if f[7] != "" {
			fs.MarkDeprecated(f[1], f[7])
		}
		if len(f) > 8 && f[8] != "" {
			fs.SetAnnotation(f[1], f[8], f[9:])
		}
	}
	for _, ch := range n.C {
		c.AddCommand(tcBuild(ch))
	}
	return c
}

func tcFollow(c *cobra.Command, path []int) *cobra.Command {
	for _, i := range path {
		c = c.Commands()[i]
	}
	return c
}

