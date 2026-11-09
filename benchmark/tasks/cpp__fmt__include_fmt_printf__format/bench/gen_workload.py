"""Seeded workload generator for basic_printf_context::format (fmt). Usage: python3 gen_workload.py <out_dir>

Each line is one case: <reps> TAB <item> TAB <item> ...   (reps = how many times the driver repeats the batch)
item = <format string> | <arg> | <arg> ...      ('|' separates, so the format strings contain no '|')
arg = <type>:<value>  with type  i int, u unsigned, l long, L long long, U unsigned long, V unsigned long long, c char, a signed char,
      h short, H unsigned short, b bool (0/1), d double, w long double, s C string, n null C string, p void* (only the null pointer, value 0)
The driver builds a printf argument list from the typed values and runs the library's printf entry point (which constructs
basic_printf_context and calls format()). It records the produced text or the message of the thrown format_error.
S: handcrafted items (every flag, width, precision, length modifier, positional arguments, escapes, every error path);
M/L: batches of random well-formed conversions (a few percent use positional arguments), M/L contain no error cases.
"""
import random, sys
from pathlib import Path

HAND = [
    "plain text", "%%", "100%% sure", "%d|i:42", "%5d|i:42", "%-5d|i:42", "%05d|i:-42", "%+d|i:42", "% d|i:42", "%x|i:255", "%#x|i:255", "%#X|i:255", "%o|i:64", "%#o|i:64", "%.5d|i:42",
    "%7.5d|i:-42", "%#10.5x|i:66", "%u|i:-1", "%i|i:7", "%c|i:65", "%c|c:z", "%5c|c:z", "%s|s:hello", "%10s|s:hello", "%-10s|s:hello", "%.3s|s:hello", "%10.3s|s:hello", "%s|n:", "%p|p:0", "%s|b:1", "%d|b:1", "%5.2f|d:3.14159",
    "%e|d:12345.678", "%E|d:0.000123", "%g|d:100000", "%g|d:1e10", "%G|d:1e-10", "%a|d:1.5", "%A|d:1.5", "%.0f|d:2.5", "%f|d:1e22", "%+.2f|d:0", "%010.3f|d:-3.14159", "%#.0f|d:3", "%f|w:2.5", "%.3Lf|w:3.14159",
    "%hhd|i:300", "%hd|i:70000", "%ld|l:-5", "%lld|L:-5", "%llu|V:18446744073709551615", "%lu|U:123", "%zu|U:99", "%jd|L:-9", "%td|l:77", "%hhu|i:-1", "%hu|i:-1", "%hhx|i:511", "%lx|l:255", "%hhd|a:-5",
    "%1$d|i:42", "%2$d %1$s|s:a|i:7", "%1$s%2$s%1$s|s:abra|s:cad", "%1$5d|i:42", "%1$-5d|i:42", "%*d|i:5|i:42", "%*d|i:-5|i:42", "%.*d|i:5|i:42", "%.*d|i:-5|i:42", "%*.*f|i:10|i:2|d:3.14159",
    "%c%c%c|c:a|c:b|c:c", "%d %s %f|i:1|s:x|d:2.5", "a%db%sc|i:1|s:x", "%.d|i:0", "%.0d|i:0", "%.s|s:abc", "%.f|d:2.7", "%#.d|i:0", "%0-5d|i:42", "%-05d|i:42", "%+05d|i:42", "% 05d|i:42", "%#05x|i:255", "%05s|s:ab", "%0c|c:x",
    "%05d|i:-7", "%-+5d|i:3", "% +d|i:3", "%+ d|i:3", "%#x|i:0", "%#o|i:0", "%#.3o|i:8", "%#b|i:5", "%b|i:5", "%08.3f|d:-1.5", "%+g|d:0.5", "%#g|d:1", "%e|d:0", "%-5s|s:ab",
    # error paths
    "%d", "%d|i:1", "%2$d|i:42", "%0$d|i:42", "%1$d%d|i:1|i:2", "%d%1$d|i:1|i:2", "%1$d%|i:1|i:2", "%d%1$|i:1|i:2", "%2147483648$d|i:42", "%99999999999d|i:1", "%*d|u:2147483648|i:1", "%.*d|d:1.5|i:1", "%*d|d:1.5|i:1", "%*d", "%.*d",
    "%|i:1", "%5|i:1", "%.|i:1", "%l|i:1", "%ll|i:1", "%hh|i:1", "%5|s:a", "%-|d:1.5", "%d%|i:1|i:2", "%", "%5", "%.", "%5-5d|i:42", "%d|s:abc", "%s|i:5", "%f|i:1", "%q|i:1", "%ld|s:x", "%c|d:1.5", "%.3d|s:abc", "%2$", "%1$|i:1", "%p|i:1",
]

CONV = {
    "i": ["d", "i", "u", "x", "X", "o", "c"], "u": ["u", "x", "X", "o", "d"], "l": ["ld", "li", "lu", "lx", "lo"], "L": ["lld", "llu", "llx"], "U": ["lu", "lx"], "V": ["llu", "llx"],
    "h": ["hd", "hu"], "a": ["hhd", "hhu"], "c": ["c", "d"], "d": ["f", "F", "e", "E", "g", "G", "a", "A"], "s": ["s"], "b": ["s", "d"], "p": ["p"],
}


def rnd_arg(rng, t):
    if t in "iul":
        return "%s:%d" % (t, rng.choice([0, 1, -1, 42, -42, 255, 65, 1000000, -2147483647, rng.randrange(-2 ** 31, 2 ** 31)]) if t != "u" else rng.choice([0, 1, 255, 4000000000, rng.randrange(0, 2 ** 32)]))
    if t == "L":
        return "L:%d" % rng.choice([0, -1, 1 << 40, -(1 << 50), rng.randrange(-2 ** 62, 2 ** 62)])
    if t in "UV":
        return "%s:%d" % (t, rng.choice([0, 1, 1 << 40, rng.randrange(0, 2 ** 63)]))
    if t == "h":
        return "h:%d" % rng.randrange(-32768, 32768)
    if t == "a":
        return "a:%d" % rng.randrange(-128, 128)
    if t == "c":
        return "c:" + rng.choice("abcXYZ09 ~")
    if t == "d":
        return "d:%s" % repr(rng.choice([0.0, 1.5, 2.5, 0.1, 100.0, 12345.6789, 1e-5, 1e15, rng.uniform(-1000, 1000), rng.uniform(0, 1) * 10 ** rng.randrange(-10, 11)]))
    if t == "s":
        return "s:" + "".join(rng.choice("abcdefghij XYZ_") for _ in range(rng.randrange(0, 12)))
    if t == "b":
        return "b:%d" % rng.randrange(2)
    return "p:0"


def conversion(rng):
    """returns (spec_without_percent_and_type, type_char, argtype, extra_args)"""
    t = rng.choice(list(CONV))
    conv = rng.choice(CONV[t])
    flags = "".join(rng.choice("-+ #0") for _ in range(rng.choice([0, 0, 0, 1, 1, 2])))
    extras = []
    width = ""
    r = rng.random()
    if r < 0.4:
        width = str(rng.randrange(1, 25))
    elif r < 0.5:
        width = "*"
        extras.append("i:%d" % rng.choice([5, 12, -8, 20, 0]))
    prec = ""
    r = rng.random()
    if conv in ("c", "p"):
        pass
    elif r < 0.35:
        prec = "." + str(rng.randrange(0, 14))
    elif r < 0.45:
        prec = ".*"
        extras.append("i:%d" % rng.choice([0, 3, 8, -1, 12]))
    if t == "s":
        flags = flags.replace("#", "").replace("+", "").replace(" ", "")
    return flags, width, prec, conv, t, extras


def text(rng):
    return "".join(rng.choice("abcdefgh .,:;-=") for _ in range(rng.choice([0, 0, 1, 3, 6])))


def make_item(rng, nconv):
    positional = rng.random() < 0.12
    fmt = text(rng)
    args = []
    order = []
    for k in range(nconv):
        flags, width, prec, conv, t, extras = conversion(rng)
        a = rnd_arg(rng, t)
        if positional:
            fmt += "%%%d$%s%s%s%s" % (k + 1, flags, width.replace("*", ""), prec.replace(".*", ".3"), conv)
            args.append(a)
        else:
            fmt += "%" + flags + width + prec + conv
            args.extend(extras)
            args.append(a)
        fmt += text(rng)
        if rng.random() < 0.08:
            fmt += "%%"
    return "|".join([fmt] + args)


def lines(size, rng):
    out = []
    if size == "S":
        items = list(HAND)
        for i in range(0, len(items), 10):
            out.append("1\t" + "\t".join(items[i:i + 10]))
        for _ in range(4):
            out.append("1\t" + "\t".join(make_item(rng, rng.randrange(1, 5)) for _ in range(10)))
        return out
    reps, ncase, per = {"M": (10, 20, 300), "L": (10, 20, 3000)}[size]
    for _ in range(ncase):
        out.append("%d\t" % reps + "\t".join(make_item(rng, rng.choice([1, 2, 3, 4, 6])) for _ in range(per)))
    return out


if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    for i, size in enumerate(["S", "M", "L"]):
        rng = random.Random(20191202 + i)
        (out_dir / ("workload_%s.txt" % size)).write_text("\n".join(lines(size, rng)) + "\n", encoding="utf-8")
