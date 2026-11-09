// Time Capsulo bench driver for `lexer::scan`. argv: <size> <repeat> <mode>   (mode = check | time)
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

typedef nlohmann::detail::lexer<json> Lexer;
typedef Lexer::token_type TT;

struct Tok { int kind; uint64_t v; size_t pos; size_t line; };
struct Case { int reps; std::string text; };
static std::vector<Case> g_cases;
static std::unique_ptr<Lexer> g_lx;
static std::vector<Tok> g_toks;
static std::string g_err;

// Workload line: reps TAB input bytes as lowercase hex
static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    c.text = tcb::unhex(f[1]);
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t i) {
  g_lx.reset(new Lexer(nlohmann::detail::input_adapter_t(nlohmann::detail::input_adapter(g_cases[i].text))));
  g_toks.clear(); g_toks.reserve(g_cases[i].text.size() / 2 + 8);
  g_err.clear();
}

static uint64_t exec(size_t) {
  uint64_t sum = 0;
  for (;;) {
    TT t = g_lx->scan();
    Tok k;
    k.kind = static_cast<int>(t);
    k.v = 0;
    switch (t) {
      case TT::value_string: k.v = g_lx->get_string().size(); break;
      case TT::value_integer: { json::number_integer_t x = g_lx->get_number_integer(); memcpy(&k.v, &x, sizeof x); break; }
      case TT::value_unsigned: k.v = g_lx->get_number_unsigned(); break;
      case TT::value_float: { json::number_float_t x = g_lx->get_number_float(); memcpy(&k.v, &x, sizeof x); break; }
      default: break;
    }
    nlohmann::detail::position_t p = g_lx->get_position();
    k.pos = p.chars_read_total;
    k.line = p.lines_read;
    g_toks.push_back(k);
    sum += static_cast<uint64_t>(k.kind) + k.v + k.pos;
    if (t == TT::end_of_input) break;
    if (t == TT::parse_error) { g_err = g_lx->get_error_message(); break; }
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  for (size_t k = 0; k < g_toks.size(); ++k) { h.u64(g_toks[k].kind); h.u64(g_toks[k].v); h.u64(g_toks[k].pos); h.u64(g_toks[k].line); }
  h.str(g_err);
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
