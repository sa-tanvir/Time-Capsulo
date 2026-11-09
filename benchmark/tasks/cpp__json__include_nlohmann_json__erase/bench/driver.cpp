// Time Capsulo bench driver for `basic_json::erase(range)`. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with -O2 -std=c++11 -fno-access-control -I/w/include (nlohmann/json 3.7.2, split headers).
#include <nlohmann/json.hpp>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <stdint.h>

namespace tcb {
struct Hash {
  uint64_t h;
  Hash() : h(1469598103934665603ULL) {}
  void add(const void* p, size_t n) {
    const unsigned char* c = static_cast<const unsigned char*>(p);
    for (size_t i = 0; i < n; ++i) { h ^= c[i]; h *= 1099511628211ULL; }
  }
  void u64(uint64_t v) { add(&v, 8); }
  void str(const char* s, size_t n) { u64(n); add(s, n); }
  void str(const std::string& s) { str(s.data(), s.size()); }
  std::string hex() const { char b[32]; snprintf(b, sizeof b, "%016llx", static_cast<unsigned long long>(h)); return b; }
};

inline std::vector<std::string> split_tabs(const std::string& line) {
  std::vector<std::string> out;
  size_t pos = 0;
  for (;;) {
    size_t t = line.find('\t', pos);
    if (t == std::string::npos) { out.push_back(line.substr(pos)); break; }
    out.push_back(line.substr(pos, t - pos));
    pos = t + 1;
  }
  return out;
}

inline std::vector<std::string> load_lines(const char* size) {
  const char* task = getenv("TC_TASK");
  std::string path = std::string(task ? task : "/task") + "/bench/workload_" + size + ".txt";
  std::ifstream in(path.c_str(), std::ios::binary);
  if (!in) { fprintf(stderr, "cannot open %s\n", path.c_str()); exit(2); }
  std::vector<std::string> lines;
  std::string line;
  while (std::getline(in, line)) {
    if (!line.empty() && line[line.size() - 1] == '\r') line.erase(line.size() - 1);
    if (!line.empty()) lines.push_back(line);
  }
  return lines;
}

inline int hexv(char c) { return c <= '9' ? c - '0' : c - 'a' + 10; }
// Decode a lowercase hex string into raw bytes.
inline std::string unhex(const std::string& s) {
  std::string o;
  for (size_t i = 0; i + 1 < s.size(); i += 2) o += static_cast<char>(hexv(s[i]) * 16 + hexv(s[i + 1]));
  return o;
}
}  // namespace tcb

using json = nlohmann::json;

// Workload line: reps TAB kind TAB json TAB ops      kind = pos | range
//   ops is a comma separated list; one op = an iterator token (pos) or two tokens joined by ':' (range).
//   token: B = a.begin(), E = a.end(), X = begin() of a different json value (never part of `a`),
//          integer i = the i-th element (array: position at the time of the call; object: i-th member of the original object, ascending key order).
struct Op { char t[2]; long v[2]; };
struct Case { int reps; bool range; std::string text; std::vector<Op> ops; };
struct Res { long idx; std::string s; };
static std::vector<Case> g_cases;
static json g_a, g_x;
static std::vector<json::iterator> g_pre;
static std::vector<Res> g_res;
static std::vector<std::string> g_err;

static void parse_tok(const std::string& s, char& t, long& v) {
  if (s == "B" || s == "E" || s == "X") { t = s[0]; v = 0; } else { t = 'N'; v = atol(s.c_str()); }
}

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    c.range = f[1] == "range";
    c.text = f[2];
    size_t pos = 0;
    const std::string& o = f[3];
    while (pos <= o.size()) {
      size_t e = o.find(',', pos);
      if (e == std::string::npos) e = o.size();
      std::string item = o.substr(pos, e - pos);
      Op op;
      op.t[1] = 'B'; op.v[1] = 0;
      size_t colon = item.find(':');
      if (colon == std::string::npos) parse_tok(item, op.t[0], op.v[0]);
      else { parse_tok(item.substr(0, colon), op.t[0], op.v[0]); parse_tok(item.substr(colon + 1), op.t[1], op.v[1]); }
      c.ops.push_back(op);
      pos = e + 1;
    }
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static json::iterator tok(char t, long v, int slot) {
  if (t == 'B') return g_a.begin();
  if (t == 'E') return g_a.end();
  if (t == 'X') return g_x.begin();
  if (g_a.is_object()) return g_pre[v];
  return g_a.begin() + v;
}

static void reset(size_t i) {
  const Case& c = g_cases[i];
  g_a = json::parse(c.text);
  g_x = json::parse("[0]");
  g_res.clear(); g_res.reserve(c.ops.size());
  g_err.clear();
  g_pre.clear();
  if (g_a.is_object()) {
    // iterators of the original members (std::map iterators stay valid while other members are erased)
    for (json::iterator it = g_a.begin(); it != g_a.end(); ++it) g_pre.push_back(it);
    g_pre.push_back(g_a.end());
  }
}

static uint64_t exec(size_t i) {
  const Case& c = g_cases[i];
  uint64_t sum = 0;
  for (size_t k = 0; k < c.ops.size(); ++k) {
    const Op& op = c.ops[k];
    Res r; r.idx = -2;
    try {
      json::iterator res;
      if (c.range) res = g_a.erase(tok(op.t[0], op.v[0], 0), tok(op.t[1], op.v[1], 1));
      else res = g_a.erase(tok(op.t[0], op.v[0], 0));
      if (res == g_a.end()) r.idx = -1;
      else if (g_a.is_object()) { r.idx = 0; r.s = res.key(); }
      else r.idx = res - g_a.begin();
    } catch (json::exception& e) {
      g_err.push_back(e.what());
      r.idx = -3;
    }
    sum += static_cast<uint64_t>(r.idx + 4) + r.s.size();
    g_res.push_back(r);
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  h.str(g_a.dump());
  for (size_t k = 0; k < g_res.size(); ++k) { h.u64(static_cast<uint64_t>(g_res[k].idx)); h.str(g_res[k].s); }
  for (size_t k = 0; k < g_err.size(); ++k) h.str(g_err[k]);
}

// hooks provided above: prepare(lines), ncases(), reps(i), reset(i) [untimed], exec(i) [timed, returns checksum], digest(i, h)
int main(int argc, char** argv) {
  if (argc < 4) { fprintf(stderr, "usage: driver <size> <repeat> <mode>\n"); return 2; }
  const char* size = argv[1];
  int repeat = atoi(argv[2]);
  std::string mode = argv[3];

  prepare(tcb::load_lines(size));
  size_t n = ncases();

  if (mode == "check") {
    tcb::Hash h;
    for (size_t i = 0; i < n; ++i) {
      reset(i);
      exec(i);
      digest(i, h);
    }
    printf("{\"cases\": %zu, \"output_digest\": \"%s\"}\n", n, h.hex().c_str());
    return 0;
  }

  uint64_t sink = 0;
  double elapsed = 0;
  typedef std::chrono::steady_clock clk;
  for (int r = 0; r < repeat; ++r)
    for (size_t i = 0; i < n; ++i)
      for (int k = 0, kr = reps(i); k < kr; ++k) {
        reset(i);
        clk::time_point t0 = clk::now();
        sink += exec(i);
        clk::time_point t1 = clk::now();
        elapsed += std::chrono::duration<double>(t1 - t0).count();
      }
  fprintf(stderr, "checksum %llu\n", static_cast<unsigned long long>(sink));
  printf("{\"cases\": %zu, \"repeat\": %d, \"elapsed_s\": %.6f}\n", n, repeat, elapsed);
  return 0;
}
