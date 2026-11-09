package gjson

// Time Capsulo bench driver for arrayOrMap. It is copied into the package as zz_tcbench_test.go.
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
	"sort"
	"strings"
)

func tcFmtResult(r Result) string {
	return fmt.Sprintf("{%d %q %q %s %d}", r.Type, r.Raw, r.Str, strconv.FormatFloat(r.Num, 'g', -1, 64), r.Index)
}

func tcFmtValue(b *strings.Builder, v interface{}) {
	switch x := v.(type) {
	case nil:
		b.WriteString("null")
	case bool:
		fmt.Fprintf(b, "%v", x)
	case float64:
		b.WriteString(strconv.FormatFloat(x, 'g', -1, 64))
	case string:
		fmt.Fprintf(b, "%q", x)
	case []interface{}:
		if x == nil {
			b.WriteString("nil[]")
			return
		}
		b.WriteString("[")
		for i, e := range x {
			if i > 0 {
				b.WriteString(",")
			}
			tcFmtValue(b, e)
		}
		b.WriteString("]")
	case map[string]interface{}:
		if x == nil {
			b.WriteString("nil{}")
			return
		}
		keys := make([]string, 0, len(x))
		for k := range x {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		b.WriteString("{")
		for i, k := range keys {
			if i > 0 {
				b.WriteString(",")
			}
			fmt.Fprintf(b, "%q:", k)
			tcFmtValue(b, x[k])
		}
		b.WriteString("}")
	default:
		fmt.Fprintf(b, "?%T", x)
	}
}

func tcFmtAOM(r arrayOrMapResult) string {
	var b strings.Builder
	fmt.Fprintf(&b, "vc=%d a=", r.vc)
	if r.a == nil {
		b.WriteString("nil")
	} else {
		fmt.Fprintf(&b, "%d[", len(r.a))
		for _, e := range r.a {
			b.WriteString(tcFmtResult(e))
		}
		b.WriteString("]")
	}
	b.WriteString(" o=")
	if r.o == nil {
		b.WriteString("nil")
	} else {
		keys := make([]string, 0, len(r.o))
		for k := range r.o {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		fmt.Fprintf(&b, "%d{", len(r.o))
		for _, k := range keys {
			fmt.Fprintf(&b, "%q:%s", k, tcFmtResult(r.o[k]))
		}
		b.WriteString("}")
	}
	b.WriteString(" ai=")
	if r.ai == nil {
		b.WriteString("nil")
	} else {
		tcFmtValue(&b, r.ai)
	}
	b.WriteString(" oi=")
	if r.oi == nil {
		b.WriteString("nil")
	} else {
		tcFmtValue(&b, r.oi)
	}
	return b.String()
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
	vcs := make([]byte, ncases)
	vals := make([]bool, ncases)
	for k, c := range doc.Cases {
		res[k] = Result{Type: JSON, Raw: c[0].(string)}
		vcs[k] = byte(int(c[1].(float64)))
		vals[k] = c[2].(bool)
	}
	if mode == "check" {
		h := sha256.New()
		for k := range res {
			fmt.Fprintln(h, tcFmtAOM(res[k].arrayOrMap(vcs[k], vals[k])))
		}
		fmt.Printf("{\"cases\": %d, \"output_digest\": \"%s\"}\n", ncases, hex.EncodeToString(h.Sum(nil)))
		return
	}
	sink := 0
	t0 := time.Now()
	for r := 0; r < repeat; r++ {
		for k := range res {
			r := res[k].arrayOrMap(vcs[k], vals[k])
			sink += len(r.a) + len(r.ai) + len(r.o) + len(r.oi)
		}
	}
	el := time.Since(t0).Seconds()
	fmt.Fprintln(os.Stderr, "sink", sink)
	fmt.Printf("{\"cases\": %d, \"repeat\": %d, \"elapsed_s\": %.9f}\n", ncases, repeat, el)
}
