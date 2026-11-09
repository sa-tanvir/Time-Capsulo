#!/usr/bin/env python3
"""Summarise `tc.py run` records (JSON lines) per label (model).

Usage: .venv/bin/python harness/summarize.py results.jsonl [--human human]

Prints, per label: number of tasks, pass rate, outcome counts, and - on tasks where both the label and the
human reference passed - the geometric mean of (label time / human time) and (label peak memory / human
peak memory) per workload size. Ratios < 1 mean the model's code was faster / used less memory."""
import argparse, collections, json, math


def gmean(xs):
    xs = [x for x in xs if x and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results"); ap.add_argument("--human", default="human")
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.results) if l.strip()]
    by = collections.defaultdict(dict)  # label -> task -> latest record
    for r in recs:
        by[r.get("label", "?")][r["task_id"]] = r
    human = by.get(a.human, {})
    for label, tasks in sorted(by.items()):
        n = len(tasks)
        st = collections.Counter(r["status"] for r in tasks.values())
        print(f"\n== {label}: {n} tasks, pass rate {st['passed'] / n:.1%}")
        print("   outcomes: " + ", ".join(f"{k}={v}" for k, v in st.most_common()))
        if label == a.human or not human:
            continue
        for size in ("S", "M", "L"):
            t_ratio, m_ratio = [], []
            for tid, r in tasks.items():
                h = human.get(tid)
                if r["status"] != "passed" or not h or h["status"] != "passed":
                    continue
                e, he = r.get("efficiency", {}).get(size), h.get("efficiency", {}).get(size)
                if e and he and he["per_pass_s_median"]:
                    t_ratio.append(e["per_pass_s_median"] / he["per_pass_s_median"])
                    if he.get("peak_rss_kb_median"):
                        m_ratio.append(e["peak_rss_kb_median"] / he["peak_rss_kb_median"])
            if t_ratio:
                print(f"   {size}: paired tasks={len(t_ratio)}  time ratio (gmean)={gmean(t_ratio):.3f}"
                      f"  memory ratio (gmean)={gmean(m_ratio) or float('nan'):.3f}")


if __name__ == "__main__":
    main()
