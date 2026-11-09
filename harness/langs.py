"""Language adapters: function extents, stubs, static filters, prompt context.

extent(src_lines, start_line, lizard_end_line, name) -> dict | None
    start      1-based first line of the function (replaced from column 0)
    end        1-based last line (the line holding the closing brace / last body line)
    suffix     text on the end line after the function (kept on injection), incl. newline
    sig_end    (line_idx0, col) just past the signature terminator (':' or '{')
"""
import re

STUB_MARK = "TC_STUB"


def _indent(line):
    return re.match(r"[ \t]*", line).group(0)


def _rest_after_signature(src, start):
    """Body text (everything after the first line) - used for recursion detection."""
    return "".join(src[start:])


# ----------------------------------------------------------------- base

class Lang:
    name = ""
    ext = ""
    backtick = False
    loop_re = re.compile(r"\b(for|while)\b")
    nondet_re = None
    import_re = None
    comment = "//"

    def strip_comments_strings(self, text):
        """Code with comments, docstrings and string literals blanked out (for the static filters)."""
        if self.name == "python":
            text = re.sub(r'(?s)("""|\'\'\')(.*?)\1', " ", text)
            text = re.sub(r"#[^\n]*", " ", text)
        else:
            text = re.sub(r"(?s)/\*.*?\*/", " ", text)
            text = re.sub(r"//[^\n]*", " ", text)
            if self.backtick:
                text = re.sub(r"`[^`]*`", " ", text)
        return re.sub(r'"(\\.|[^"\\\n])*"|\'(\\.|[^\'\\\n])*\'', " ", text)

    def has_loop(self, body, name):
        code = self.strip_comments_strings(body)
        if self.loop_re.search(code):
            return True
        short = name.split("::")[-1].split(".")[-1]
        first_nl = code.find("\n")
        # recursion: a call to its own name that is not a method call on another object (x.name(...))
        return re.search(r"(?<![.\w])" + re.escape(short) + r"\s*\(", code[first_nl + 1:]) is not None

    def nondeterminism(self, body):
        if not self.nondet_re:
            return ""
        m = self.nondet_re.search(body)
        return m.group(0).strip() if m else ""

    def context(self, src, start, end, rel, funcs):
        imports, i = [], 0
        while i < len(src):
            l = src[i]
            if self.import_re and self.import_re.match(l):
                stmt = [l.rstrip()]
                depth = l.count("(") - l.count(")") + l.count("{") - l.count("}")
                while depth > 0 and i + 1 < len(src):
                    i += 1
                    stmt.append(src[i].rstrip())
                    depth += src[i].count("(") - src[i].count(")") + src[i].count("{") - src[i].count("}")
                imports.append("\n".join(stmt))
            i += 1
        others = sorted({f.long_name for f in funcs if f.start_line != start
                         and not re.match(r"__\w+__$", f.name.split(".")[-1].split("::")[-1])})
        enclosing = self.enclosing(src, start)
        out = [f"# Context for the function to implement\n",
               f"- **Language:** {self.name}",
               f"- **File:** `{rel}`"]
        if enclosing:
            out.append(f"- **Enclosing scope:** `{enclosing}`")
        out.append("\n## Imports / includes available in this file\n")
        out.append("```\n" + ("\n".join(imports[:60]) or "(none)") + "\n```")
        out.append("\n## Other functions defined in the same file (signatures only; you may call them)\n")
        out.append("```\n" + ("\n".join(others[:200]) or "(none)") + "\n```\n")
        return "\n".join(out)

    def enclosing(self, src, start):
        return ""


# ----------------------------------------------------------------- python

class Python(Lang):
    name, ext, comment = "python", ".py", "#"
    loop_re = re.compile(r"\b(for|while)\b")
    nondet_re = re.compile(r"\b(random\.|time\.time|time\.sleep|datetime\.now|datetime\.today|date\.today"
                           r"|os\.environ|socket\.|threading\.|uuid\.|open\()")
    import_re = re.compile(r"^(import |from \S+ import )")

    def signature_span(self, src, start, name):
        depth = 0
        i = start - 1
        if not re.match(r"\s*(async\s+)?def\b", src[i]):
            return None
        while i < len(src):
            line = src[i]
            j = 0
            while j < len(line):
                c = line[j]
                if c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                elif c == "#":
                    break
                elif c in "'\"":
                    q = c
                    j += 1
                    while j < len(line) and line[j] != q:
                        j += 2 if line[j] == "\\" else 1
                elif c == ":" and depth == 0:
                    return (i, j + 1)
                j += 1
            i += 1
            if i - start > 30:
                return None
        return None

    def extent(self, src, start, lz_end, name):
        sig = self.signature_span(src, start, name)
        if sig is None:
            return None
        end = lz_end
        while end > start and not src[end - 1].strip():
            end -= 1
        return {"start": start, "end": end, "suffix": "\n", "sig_end": sig}

    def _body_indent(self, src, sig, start):
        for l in src[sig[0] + 1:]:
            if l.strip():
                return _indent(l)
        return _indent(src[start - 1]) + "    "

    def make_stub(self, src, ext, for_prompt=False):
        start = ext["start"]
        li, col = ext["sig_end"]
        sig = "".join(src[start - 1:li]) + src[li][:col]
        bi = self._body_indent(src, ext["sig_end"], start)
        if for_prompt:
            return f"{sig}\n{bi}raise NotImplementedError  # TODO: implement according to the specification\n"
        return f"{sig}\n{bi}raise NotImplementedError('{STUB_MARK}')\n"

    def enclosing(self, src, start):
        ind = len(_indent(src[start - 1]))
        for l in reversed(src[:start - 1]):
            if l.strip() and len(_indent(l)) < ind and re.match(r"\s*class\s+\w+", l):
                return l.strip().rstrip(":")
            if l.strip() and len(_indent(l)) == 0:
                break
        return ""


# ----------------------------------------------------------------- brace languages

class Brace(Lang):
    throw = ""
    char_literals = True     # '...' is a char/string literal
    backtick = False         # `...` strings (Go raw, JS template)
    js_regex = False
    rust = False

    def _scan(self, text, pos, stop_at_open=False):
        """Scan text from pos. If stop_at_open, return index of first '{' at paren depth 0.
        Otherwise text[pos] must be '{' and the index of its matching '}' is returned."""
        n = len(text)
        depth_paren = 0
        depth = 0
        i = pos
        prev_sig = "("  # previous significant char, for JS regex detection
        prev_word = ""
        while i < n:
            c = text[i]
            nx = text[i + 1] if i + 1 < n else ""
            if c == "/" and nx == "/":
                i = text.find("\n", i)
                if i < 0:
                    return None
                continue
            if c == "/" and nx == "*":
                i = text.find("*/", i + 2)
                if i < 0:
                    return None
                i += 2
                continue
            if self.rust and c == "r" and re.match(r'r#*"', text[i:i + 10]) and not (text[i - 1].isalnum() or text[i - 1] == "_"):
                m = re.match(r'r(#*)"', text[i:])
                close = '"' + m.group(1)
                j = text.find(close, i + len(m.group(0)))
                if j < 0:
                    return None
                i = j + len(close)
                prev_sig = '"'
                continue
            if c == '"' or (c == "'" and self.char_literals) or (c == "`" and self.backtick):
                if c == "'" and self.rust and not re.match(r"'(\\.|\\u\{[0-9a-fA-F]+\}|[^\\'])'", text[i:i + 12]):
                    i += 1  # lifetime
                    continue
                if c == "'" and not self.rust and self.name == "cpp" and text[i - 1].isdigit():
                    i += 1  # C++14 digit separator
                    continue
                j = i + 1
                while j < n and text[j] != c:
                    if text[j] == "\\" and c != "`" or (text[j] == "\\" and self.js_regex):
                        j += 2
                        continue
                    if c != "`" and text[j] == "\n" and self.name != "go":
                        break
                    j += 1
                i = j + 1
                prev_sig = '"'
                continue
            if self.js_regex and c == "/" and (prev_sig in "(,=:[!&|?{};+-*%<>~^" or prev_word in ("return", "typeof", "case", "in", "of")):
                j = i + 1
                in_class = False
                while j < n and text[j] != "\n":
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == "[":
                        in_class = True
                    elif text[j] == "]":
                        in_class = False
                    elif text[j] == "/" and not in_class:
                        break
                    j += 1
                i = j + 1
                prev_sig = "a"
                continue
            if c.isalpha() or c == "_":
                m = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", text[i:])
                prev_word = m.group(0)
                prev_sig = "a"
                i += len(prev_word)
                continue
            if not c.isspace():
                prev_sig = c
                prev_word = ""
            if c == "(":
                depth_paren += 1
            elif c == ")":
                depth_paren -= 1
            elif c == "{":
                if stop_at_open and depth_paren == 0:
                    return i
                depth += 1
            elif c == "}":
                depth -= 1
                if not stop_at_open and depth == 0:
                    return i
            elif c == ";" and stop_at_open and depth_paren == 0:
                return None  # declaration without body
            i += 1
        return None

    def signature_span(self, src, start, name):
        e = self.extent(src, start, None, name)
        return e["sig_end"] if e else None

    def extent(self, src, start, lz_end, name):
        offs = [0]
        for l in src:
            offs.append(offs[-1] + len(l))
        text = "".join(src)
        p0 = offs[start - 1]
        ob = self._scan(text, p0, stop_at_open=True)
        if ob is None or ob - p0 > 3000:
            return None
        cb = self._scan(text, ob)
        if cb is None:
            return None

        def loc(p):
            # 0-based line index containing absolute offset p
            lo, hi = 0, len(offs) - 1
            while lo < hi - 1:
                mid = (lo + hi) // 2
                if offs[mid] <= p:
                    lo = mid
                else:
                    hi = mid
            return lo

        ol, cl = loc(ob), loc(cb)
        suffix = src[cl][cb - offs[cl] + 1:]
        if lz_end is not None and abs((cl + 1) - lz_end) > 2:
            return None  # disagreement with lizard: skip rather than risk a wrong span
        return {"start": start, "end": cl + 1, "suffix": suffix if suffix else "\n",
                "sig_end": (ol, ob - offs[ol] + 1)}

    def make_stub(self, src, ext, for_prompt=False):
        start = ext["start"]
        li, col = ext["sig_end"]
        sig = "".join(src[start - 1:li]) + src[li][:col]
        ind = _indent(src[start - 1])
        if for_prompt:
            return f"{sig}\n{ind}    {self.comment} TODO: implement according to the specification\n{ind}}}"
        return f"{sig}\n{ind}    {self.throw}\n{ind}}}"


class Cpp(Brace):
    name, ext = "cpp", ".cpp"
    throw = f'throw "{STUB_MARK}";'
    loop_re = re.compile(r"\b(for|while|do)\b|std::(for_each|transform|accumulate|find_if)")
    nondet_re = re.compile(r"\b(rand\s*\(|std::random_device|std::mt19937|chrono::|time\s*\(|getenv|std::thread|fopen|[io]?fstream)")
    import_re = re.compile(r"^\s*#\s*include\b")


class Java(Brace):
    name, ext = "java", ".java"
    throw = f'throw new UnsupportedOperationException("{STUB_MARK}");'
    loop_re = re.compile(r"\b(for|while|do)\b|\.(forEach|stream)\(")
    nondet_re = re.compile(r"\b(new Random|Math\.random|currentTimeMillis|nanoTime|new Date\(\)|Thread\.|System\.getenv|new File)")
    import_re = re.compile(r"^import\s")

    def enclosing(self, src, start):
        for l in reversed(src[:start - 1]):
            m = re.match(r"\s*(public\s+|abstract\s+|final\s+|static\s+)*(class|interface|enum)\s+\w+", l)
            if m:
                return l.strip().rstrip("{").strip()
        return ""


class Go(Brace):
    name, ext = "go", ".go"
    throw = f'panic("{STUB_MARK}")'
    backtick = True
    loop_re = re.compile(r"\bfor\b")
    nondet_re = re.compile(r"\b(rand\.|time\.Now|os\.Getenv|os\.Open|net\.|http\.Get)|\bgo\s+func\b")

    def make_stub(self, src, ext, for_prompt=False):
        if for_prompt:
            return Brace.make_stub(self, src, ext, for_prompt)
        # Sabotage stub: panic first, keep the original (now unreachable) body after it.
        # Go rejects unused imports, so dropping the body would stop the package compiling
        # whenever an import is only used inside this function.
        start, end = ext["start"], ext["end"]
        li, col = ext["sig_end"]
        sig = "".join(src[start - 1:li]) + src[li][:col]
        last = src[end - 1]
        cut = (len(last) - len(ext["suffix"]) if last.endswith(ext["suffix"]) else len(last.rstrip("\n"))) - 1
        if end - 1 == li:
            body = last[col:cut]
        else:
            body = src[li][col:] + "".join(src[li + 1:end - 1]) + last[:cut]
        return f"{sig}\n{_indent(src[start - 1])}    {self.throw}\n{body}}}"

    def context(self, src, start, end, rel, funcs):
        text = "".join(src)
        m = re.search(r"^import\s*\((.*?)\)", text, re.S | re.M)
        imps = [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else re.findall(r'^import\s+(".*?")', text, re.M)
        src2 = [f"import {i}\n" for i in imps]
        self.import_re = re.compile(r"^import ")
        return Lang.context(self, src2 + ["\n"], -1, end, rel, [f for f in funcs if f.start_line != start])


class Rust(Brace):
    name, ext = "rust", ".rs"
    throw = f'panic!("{STUB_MARK}")'
    rust = True
    loop_re = re.compile(r"\b(for|while|loop)\b|\.(iter|into_iter|chars|bytes|map|fold|for_each)\(")
    nondet_re = re.compile(r"\b(rand::|Instant::now|SystemTime|std::env|env::var|thread::spawn|File::)")
    import_re = re.compile(r"^\s*(pub\s+)?use\s")

    def enclosing(self, src, start):
        for l in reversed(src[:start - 1]):
            if re.match(r"\s*impl\b", l) or re.match(r"\s*(pub\s+)?trait\b", l):
                return l.strip().rstrip("{").strip()
            if re.match(r"(pub\s+)?(fn|struct|enum|mod)\b", l):
                break
        return ""


class JavaScript(Brace):
    name, ext = "javascript", ".js"
    throw = f"throw new Error('{STUB_MARK}');"
    backtick = True
    js_regex = True
    loop_re = re.compile(r"\b(for|while|do)\b|\.(forEach|map|reduce|filter|some|every)\(|\b(arrayEach|baseFor|baseEach|arrayMap|baseTimes)\(")
    nondet_re = re.compile(r"\b(Math\.random|Date\.now|new Date\(\)|setTimeout|setInterval|process\.env|require\(['\"]fs)")
    import_re = re.compile(r"^\s*(import\s|(var|const|let)\s+\w+\s*=\s*require\()")
    decl_re = re.compile(r"^([ \t]*)(var|let|const)\s+[A-Za-z_$][\w$]*\s*(=|,|;)")

    def context(self, src, start, end, rel, funcs):
        """JS modules keep their shared state in scope-level `var`s (option defaults, lookup
        tables, cached builtins). List those declared at the target's own scope level so the
        model knows they exist (require() lines and function definitions are listed elsewhere)."""
        out = Lang.context(self, src, start, end, rel, funcs)
        ind = _indent(src[start - 1])
        decls, i = [], 0
        while i < len(src):
            m = self.decl_re.match(src[i])
            if (start - 1 <= i < end) or not m or m.group(1) != ind or self.import_re.match(src[i]) \
                    or re.match(r"\s*(var|let|const)\s+[\w$]+\s*=\s*function\b", src[i]):
                i += 1
                continue
            stmt, depth = [], 0
            while i < len(src) and len(stmt) < 25:
                l = src[i].rstrip()
                stmt.append(l)
                # brackets inside string / regex literals (e.g. /^\/?Date\((\-?\d+)/i) don't count
                lc = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "''", l)
                lc = re.sub(r"(?<![\w$)\]])/(?![/*])(?:\\.|\[(?:\\.|[^\]\\])*\]|[^/\\\n])+/[gimsuy]*", "/r/", lc)
                depth += sum(lc.count(c) for c in "([{") - sum(lc.count(c) for c in ")]}")
                i += 1
                if depth <= 0 and l.endswith(";"):
                    break
            else:
                stmt.append(ind + "    ...")
            decls.append("\n".join(s[len(ind):] if s.startswith(ind) else s for s in stmt))
        if decls:
            out += ("\n## Variables declared at the same scope level (you may use them)\n\n```\n"
                    + "\n".join(decls[:300]) + "\n```\n")
        return out


LANGS = {c.name: c() for c in (Python, Cpp, Java, Go, Rust, JavaScript)}


def get(name):
    return LANGS[name]


# Rust: lizard 1.17 tokenises lifetimes (`'a`, `'w`) as the start of a char literal, so in files with
# lifetimes it silently loses most functions. Blank the quote of lifetimes (same length, same lines)
# before lizard sees a .rs file. Char literals ('a', '\n', '-') are untouched.
def _patch_lizard_rust_lifetimes():
    try:
        import lizard
    except ImportError:
        return
    fa = lizard.analyze_file
    orig = fa.analyze_source_code
    if getattr(orig, "_tc_rust_patch", False):
        return
    lt = re.compile(r"'(?=[A-Za-z_]\w*\b(?!'))")

    def analyze_source_code(filename, code):
        if str(filename).endswith(".rs"):
            code = lt.sub(" ", code)
        return orig(filename, code)
    analyze_source_code._tc_rust_patch = True
    fa.analyze_source_code = analyze_source_code


_patch_lizard_rust_lifetimes()
