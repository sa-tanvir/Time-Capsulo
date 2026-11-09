"""Generate one reply per task with a local Ollama model (temperature 0).

Usage: python3 harness/generate_ollama.py <ollama-model> [release_dir]
Writes replies/<model>/<task_id>.md and replies/<model>/_generation_meta.jsonl. Existing replies are kept.
"""
import json, pathlib, sys, time, urllib.request

model = sys.argv[1]
root = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else ".")
out = root / "replies" / model.replace(":", "-")
out.mkdir(parents=True, exist_ok=True)
meta = []
for task in sorted((root / "benchmark/tasks").iterdir()):
    target = out / f"{task.name}.md"
    if target.exists():
        continue
    body = json.dumps({"model": model, "prompt": (task / "prompt.md").read_text(), "stream": False,
                       "options": {"temperature": 0, "seed": 0, "num_ctx": 8192, "num_predict": 2048}}).encode()
    t = time.time()
    req = urllib.request.Request("http://localhost:11434/api/generate", body, {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=900))
    target.write_text(r["response"])
    meta.append({"task": task.name, "gen_s": round(time.time() - t, 1), "eval_count": r.get("eval_count")})
    print(task.name, meta[-1]["gen_s"], flush=True)
with (out / "_generation_meta.jsonl").open("a") as f:
    f.write("".join(json.dumps(m) + "\n" for m in meta))
