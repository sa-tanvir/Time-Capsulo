import random, sys, os
SEEDBASE = 20190411
# size -> (cases, max digit run for the mantissa, max exponent digits)
PROFILE = {"S": (300, 30, 3), "M": (1500, 3000, 4), "L": (900, 1500000, 6)}

def esc(s):
    if s is None:
        return "<null>"
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

def digits(rng, n, alpha="0123456789", lead_nonzero=True):
    s = "".join(rng.choice(alpha) for _ in range(n))
    if lead_nonzero and n > 0 and s[0] == "0":
        s = rng.choice("123456789") + s[1:]
    return s

def make(rng, big, expdig):
    """returns (pre, mid, rep, post)."""
    kind = rng.random()
    sign = rng.choice(["", "", "", "-", "+"])
    nd = rng.randint(1, 12)
    if kind < 0.18:                                     # plain integers, small to huge
        if rng.random() < 0.6:
            return (sign + digits(rng, nd), "", 1, "")
        n = rng.randint(1, big)
        return (sign + digits(rng, 1), digits(rng, 7), max(1, n // 7), digits(rng, 3))
    if kind < 0.28:                                     # octal-looking
        alpha = "01234567" if rng.random() < 0.7 else "0123456789"
        return (sign + "0" + digits(rng, rng.randint(1, 12), alpha, False), "", 1, rng.choice(["", "", "l", "L"]))
    if kind < 0.45:                                     # hex
        pfx = rng.choice(["0x", "0X", "-0x", "-0X", "#", "-#", "0x", "+0x"])
        z = "0" * rng.choice([0, 0, 0, 1, 3])
        h = rng.choice([1, 4, 7, 8, 9, 15, 16, 17, 20, 33])
        body = digits(rng, h, "0123456789abcdefABCDEF", False)
        if rng.random() < 0.2:
            body = "7" + "f" * (h - 1) if h > 1 else "7"
        return (pfx + z + body, "", 1, rng.choice(["", "", "", "L", "g"]))
    if kind < 0.55:                                     # explicit long
        n = rng.choice([1, 5, 9, 10, 11, 18, 19, 20, 25])
        return (sign + digits(rng, n), "", 1, rng.choice(["L", "l", "L", "l", "LL", "f"]))
    if kind < 0.9:                                      # decimals
        ip = digits(rng, rng.randint(0, 8), lead_nonzero=False) if rng.random() < 0.9 else ""
        fp = digits(rng, rng.randint(0, 10), lead_nonzero=False)
        if rng.random() < 0.15:
            fp = "0" * rng.randint(1, 6)
            ip = "0" * rng.randint(1, 3)
        mid, rp = "", 1
        if rng.random() < 0.3:
            mid, rp = digits(rng, 5, lead_nonzero=False), max(1, rng.randint(1, big) // 5)
        exp = ""
        if rng.random() < 0.45:
            exp = rng.choice(["e", "E"]) + rng.choice(["", "", "+", "-"]) + digits(rng, rng.randint(1, expdig), lead_nonzero=False)
            if rng.random() < 0.1:
                exp = exp[0]
        suf = rng.choice(["", "", "", "f", "F", "d", "D", "ff", "L"])
        pre = sign + ip + "." + fp
        if rng.random() < 0.08:
            pre = sign + ip + fp                       # no decimal point
            if rng.random() < 0.5:
                exp = exp or "e5"
        if mid:
            return (pre, mid, rp, exp + suf)
        return (pre + exp + suf, "", 1, "")
    # malformed variants
    base = sign + digits(rng, rng.randint(1, 9)) + rng.choice([".5", "", "e3", ".25e-2"])
    pos = rng.randint(0, len(base))
    ins = rng.choice(list("+-.eEfFdDlLxX#a_") + ["--", "e+", ".."])
    return (base[:pos] + ins + base[pos:], "", 1, "")

def ok_for_workload(s, allow_mixed):
    return True

def main(out):
    os.makedirs(out, exist_ok=True)
    for i, size in enumerate("SML"):
        rng = random.Random(SEEDBASE + i)
        count, big, expdig = PROFILE[size]
        rows = []
        if size == "S":
            fixed = ["", "   ", "0", "1", "-1", "+1", "12345", "-12345", "2147483647", "2147483648", "-2147483648", "-2147483649", "9223372036854775807", "9223372036854775808", "12345L", "12345l", "-1l", "01l", "1l", "1.1L", "1234.5", "1234.5D", "1234.5d", "1234.5F", "1234.5f", "1234.5ff", "1234.5FF", "1234.5dd", "1234.5DD", "-1234.5", "1.1E200", "1.1E20", "-1.1E200", "1.1E-200", "0.0", "+0.0", "-0.0", "0x", "0X", "0xFADE", "0Xfade", "-0xFADE", "-0Xfade", "0x8000", "0x7FFFFFFF", "0x80000000", "0xFFFFFFFF", "0x08000000", "0x00FFFFFFFF", "0x7fffffffffffffff", "0x7fffffffffffffff0", "#7fffffffffffffff", "#7fffffffffffffff0", "0x8000000000000000", "0xFFFFFFFFFFFFFFFF", "0x0000000000000000", "#", "-#1", "017777777777", "037777777777", "09", "0123", "00", "0e1", "08e1", "01.5", "08.5", "00.5", "--1.1E-700F", "-1.1E+0-7e00", "-11E+0-7e00", "1eE+00001", "1.23", "3.4028235e+38", "3.4028236e+38", "3.40282354e+38", "1.7976931348623157e+308", "1.7976931348623159e+308", "1.797693134862315759e+308", "0001.797693134862315759e+308", "-001.12", "+001.12", "003.40282354e+38", "1e-400", "1e400", "1e-50", "0e0", "0.0e0f", "0.000000000000001e-60f", "1.", ".5", "-.5", ".", "5.d", ".d", "1.e5", "1e", "1e+", "1e5", "1E5", "1e5L", "1e5f", "1e5d", "e5", "+5L", "-", "+", "1-", "1.2.3", "12a", "1_000", "0x1g", "0x1FL", "1d", "1f", "1D", "1F", "0f", "0d", "1e1f", "1e1000f", "1e-1000f", "7e-46f", "1e-46f", "0.1e-45f", "1.4e-45", "1.5e-45", "123456789012345678901234567890", "123456789012345678901234567890L", "-123456789012345678901234567890.5", "123456789.123456789", "1.00000000000000000000001", "0.1", "0.2", "16777217", "16777217.0", "3.14159265358979", "2.5e3", "-2.5E-3d", "+2.5e+3F", "1e5.0", "1.5e5.0", "0x1.5"]
            rows += [(s, "", 1, "") for s in fixed]
            rows.append((None, "", 1, ""))
        while len(rows) < count:
            pre, mid, rp, post = make(rng, big, expdig)
            if not ok_for_workload(pre + mid + post, False):
                continue
            rows.append((pre, mid, rp, post))
        with open(os.path.join(out, "workload_%s.txt" % size), "w", newline="\n") as f:
            for pre, mid, rp, post in rows:
                f.write("\t".join([esc(pre), esc(mid), str(rp), esc(post)]) + "\n")

main(sys.argv[1])
