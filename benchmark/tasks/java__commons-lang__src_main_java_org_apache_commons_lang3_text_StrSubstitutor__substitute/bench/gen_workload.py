import random, sys, os
SEEDBASE = 20190411
# size -> (cases, tokens per template, repetitions)
SIZES = {"S": (90, 8, 1), "M": (60, 70, 4), "L": (16, 40, 400)}

def esc(s):
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

WORDS = ["lorem ", "ipsum ", "dolor ", "sit ", "amet, ", "consectetur ", "x ", "$ ", "} ", "{ ", "$$ ", "# ", "< ", "> "]
# token -> relevant configs are mixed; the semantics of each syntax depends on the configuration used.
TOK = (["${animal}", "${target}", "${a}", "${b}", "${name}", "${greet}", "${n1}", "${empty}", "${num}", "${x1}", "${v2}", "${v4}", "${v5}", "${long}",
        "${pre.fix}", "${sp ace}", "${v0}", "${v1}", "${w1}", "${dollar}"] * 3 +
       ["${unknown}", "${unknown:-dflt}", "${animal:-zzz}", "${unknown:-${a}}", "${a:=q}", "${nope:=d}", "${${key}}", "${item${i}}", "${${key}:-z}",
        "$${animal}", "$${a}", "$$${a}", "${}", "${ }", "${unclosed", "$", "${", "}", "$}", "${${", "${a", "<<a>>", "<<w1>>", "!<<a>>", "<<u|def>>", "<<a|d>>", "<<<a>>",
        "!<<<a>>", "%a%", "%name%", "\\%a%", "%unknown%", "%%", "%a", "!%a%", "${n1:-q}", "${${a}}", "${${${key}}}", "$${${a}}", "${a}${b}${a}", "$${"] * 1)
CYC = ["${cyc1}", "${self}", "${v3}${cyc2}"]

def template(rng, tokens, cyc=False):
    parts = []
    for _ in range(tokens):
        r = rng.random()
        if r < 0.3:
            parts.append(rng.choice(WORDS))
        else:
            parts.append(rng.choice(TOK) + rng.choice(["", "", " ", ","]))
    if cyc:
        parts.insert(rng.randint(0, len(parts)), rng.choice(CYC))
    return "".join(parts)

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, tokens, reps = SIZES[size]
        rows = []   # cfg, text, rep, offset, trim
        if size == "S":
            S = [
                (0, "The ${animal} jumps over the ${target}.", 0, 0), (0, "", 0, 0), (0, "no variables here", 0, 0),
                (0, "${greet} and ${n1}", 0, 0), (0, "$${animal} stays", 0, 0), (0, "$$${animal}", 0, 0), (3, "$${animal} stays", 0, 0),
                (3, "$${animal} and ${animal}", 0, 0), (0, "${unknown:-fallback} ${animal:-fb}", 0, 0), (5, "${unknown:-fallback}", 0, 0),
                (0, "${}", 0, 0), (0, "${ }", 0, 0), (0, "${", 0, 0), (0, "${${", 0, 0), (0, "${${}}", 0, 0), (0, "${animal", 0, 0),
                (0, "${animal ${target}", 0, 0), (0, "x ${a} ${a", 0, 0), (0, "${cyc1}", 0, 0), (0, "ab ${self} cd", 0, 0), (0, "${a}${self}", 0, 0), (0, "$${a} ${self}", 0, 0),
                (2, "${${key}}", 0, 0), (0, "${${key}}", 0, 0), (2, "${item${i}} and ${item${i}x}", 0, 0), (2, "${unk:-${a}}", 0, 0),
                (0, "${unk:-${a}}", 0, 0), (2, "${${${key}}}", 0, 0), (1, "<<a>> ${a} !<<a>> <<u|def>> <<w1>>", 0, 0), (1, "!<<<a>>", 0, 0),
                (4, "%a% \\%a% %name%x %%", 0, 0), (4, "%a", 0, 0), (6, "$${a} ${u:=d} ${${key}:=z}", 0, 0), (6, "${a:=1}${b:=2}", 0, 0),
                (0, "abc ${a} def ${b} ghi", 4, 0), (0, "abc ${a} def ${b} ghi", 4, 5), (0, "abc ${a} def ${b} ghi", 0, 6),
                (0, "$${a}${b}", 1, 0), (0, "$${a}${b}", 0, 3), (0, "x$${a}${b}", 1, 0), (3, "x$${a}${b}", 1, 0),
                (0, "${v2}|${v4}|${v5}|${dollar}", 0, 0), (2, "${v2}|${v4}|${v5}|${dollar}", 0, 0),
                (0, "${long}${long}${long}", 0, 0), (0, "${pre.fix} ${sp ace}", 0, 0),
            ]
            for cfg, t, off, trim in S:
                rows.append((cfg, t, 1, off, trim))
        while len(rows) < count:
            cfg = rng.choice([0, 0, 0, 1, 2, 2, 3, 4, 5, 6])
            cyc = size != "L" and rng.random() < 0.04 or (size == "S" and rng.random() < 0.06)
            t = template(rng, tokens, cyc)
            off = rng.choice([0, 0, 0, 0, 1, 2, 5])
            trim = rng.choice([0, 0, 0, 0, 1, 3, 7])
            if len(t) * reps <= off + trim + 2:
                off, trim = 0, 0
            rows.append((cfg, t, reps, off, trim))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for cfg, t, rp, off, trim in rows:
                f.write("\t".join([str(cfg), esc(t), str(rp), str(off), str(trim)]) + "\n")

main(sys.argv[1])
