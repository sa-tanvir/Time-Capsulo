// Time Capsulo bench driver for `binary_reader::get_cbor_object`. argv: <size> <repeat> <mode>   (mode = check | time)
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

// ---- recording SAX handler: logs every event; the (limit+1)-th event and all later ones return false; parse errors are thrown
struct Rec {
  std::string log;
  long limit, n;
  Rec() : limit(-1), n(0) {}
  bool step() { ++n; return limit < 0 || n <= limit; }
  void q(const std::string& s) {
    char b[8];
    log += '"';
    for (size_t i = 0; i < s.size(); ++i) {
      unsigned char c = static_cast<unsigned char>(s[i]);
      if (c >= 32 && c < 127 && c != '"' && c != '\\') log += static_cast<char>(c);
      else { snprintf(b, sizeof b, "\\x%02x", c); log += b; }
    }
    log += "\";";
  }
  bool null() { log += "null;"; return step(); }
  bool boolean(bool v) { log += v ? "true;" : "false;"; return step(); }
  bool number_integer(json::number_integer_t v) { log += "int " + std::to_string(v) + ";"; return step(); }
  bool number_unsigned(json::number_unsigned_t v) { log += "uint " + std::to_string(v) + ";"; return step(); }
  bool number_float(json::number_float_t v, const std::string&) { char b[64]; snprintf(b, sizeof b, "float %a;", v); log += b; return step(); }
  bool string(std::string& v) { log += "str "; q(v); return step(); }
  bool start_object(std::size_t k) { log += "{" + (k == std::size_t(-1) ? std::string("*") : std::to_string(k)) + ";"; return step(); }
  bool key(std::string& v) { log += "key "; q(v); return step(); }
  bool end_object() { log += "};"; return step(); }
  bool start_array(std::size_t k) { log += "[" + (k == std::size_t(-1) ? std::string("*") : std::to_string(k)) + ";"; return step(); }
  bool end_array() { log += "];"; return step(); }
  bool parse_error(std::size_t, const std::string&, const nlohmann::detail::exception& ex) { throw ex; }
};

typedef nlohmann::detail::binary_reader<json, Rec> Reader;

struct Case { int reps; std::string bytes; long arg; long limit; };
static std::vector<Case> g_cases;
static std::unique_ptr<Reader> g_rd;
static Rec g_rec;
static bool g_ok;
static long g_arg;
static std::string g_err, g_str;

// Workload line: reps TAB hex TAB arg TAB limit
static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    c.bytes = tcb::unhex(f[1]);
    c.arg = f.size() > 2 ? atol(f[2].c_str()) : 0;
    c.limit = f.size() > 3 ? atol(f[3].c_str()) : -1;
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
// untimed: fresh reader positioned after the first byte (which is already "read": it is the current byte)
static void reset(size_t i) {
  g_rec = Rec();
  g_rec.limit = g_cases[i].limit;
  g_rd.reset(new Reader(nlohmann::detail::input_adapter(g_cases[i].bytes)));
  g_rd->sax = &g_rec;
  g_rd->get();
  g_arg = g_cases[i].arg;
  g_ok = false; g_err.clear(); g_str.clear();
}
static void digest(size_t, tcb::Hash& h) {
  h.u64(g_ok);
  h.str(g_rec.log);
  h.str(g_err);
  if (g_ok) { h.str(g_str); h.u64(g_rd->chars_read); }
}


static uint64_t exec(size_t) {
  try { g_ok = g_rd->get_cbor_object(static_cast<std::size_t>(g_arg)); } catch (const nlohmann::detail::exception& e) { g_err = e.what(); g_ok = false; }
  return g_str.size() + g_rec.log.size() + g_err.size() + (g_ok ? 1 : 0);
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
