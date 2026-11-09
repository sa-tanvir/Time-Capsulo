// Time Capsulo bench driver for `parse_chrono_format`. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with -O2 -std=c++11 -DFMT_HEADER_ONLY against /w/include.
#include "fmt/format.h"
#include "fmt/chrono.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <stdint.h>

namespace tcb {
struct Rng {
  uint64_t s;
  explicit Rng(uint64_t seed) : s(seed) {}
  uint64_t next() {
    s += 0x9E3779B97F4A7C15ULL;
    uint64_t z = s;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
  }
  uint64_t below(uint64_t n) { return next() % n; }
};

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

// Text fields may contain \t \n \\ escapes written as backslash sequences.
inline std::string unescape(const std::string& s) {
  std::string o;
  for (size_t i = 0; i < s.size(); ++i) {
    if (s[i] == '\\' && i + 1 < s.size()) {
      char c = s[++i];
      o += c == 't' ? '\t' : c == 'n' ? '\n' : c == '0' ? '\0' : c;
    } else o += s[i];
  }
  return o;
}
}  // namespace tcb

using namespace fmt;
using namespace fmt::internal;

// Records every callback as a mixed 64-bit value.
struct Rec {
  uint64_t acc;
  Rec() : acc(1469598103934665603ULL) {}
  void mix(uint64_t v) { acc = (acc ^ v) * 1099511628211ULL; }
  void on_text(const char* b, const char* e) {
    mix(0x1000 + static_cast<uint64_t>(e - b));
    for (; b != e; ++b) mix(static_cast<unsigned char>(*b));
  }
  void on_abbr_weekday() { mix(8192); }
  void on_full_weekday() { mix(8193); }
  void on_abbr_month() { mix(8194); }
  void on_full_month() { mix(8195); }
  void on_us_date() { mix(8196); }
  void on_iso_date() { mix(8197); }
  void on_12_hour_time() { mix(8198); }
  void on_24_hour_time() { mix(8199); }
  void on_iso_time() { mix(8200); }
  void on_am_pm() { mix(8201); }
  void on_duration_value() { mix(8202); }
  void on_duration_unit() { mix(8203); }
  void on_utc_offset() { mix(8204); }
  void on_tz_name() { mix(8205); }
  void on_dec0_weekday(numeric_system ns) { mix(12288 + static_cast<unsigned>(ns)); }
  void on_dec1_weekday(numeric_system ns) { mix(12290 + static_cast<unsigned>(ns)); }
  void on_24_hour(numeric_system ns) { mix(12292 + static_cast<unsigned>(ns)); }
  void on_12_hour(numeric_system ns) { mix(12294 + static_cast<unsigned>(ns)); }
  void on_minute(numeric_system ns) { mix(12296 + static_cast<unsigned>(ns)); }
  void on_second(numeric_system ns) { mix(12298 + static_cast<unsigned>(ns)); }
  void on_datetime(numeric_system ns) { mix(12300 + static_cast<unsigned>(ns)); }
  void on_loc_date(numeric_system ns) { mix(12302 + static_cast<unsigned>(ns)); }
  void on_loc_time(numeric_system ns) { mix(12304 + static_cast<unsigned>(ns)); }
};

struct Case { std::vector<std::string> strs; int reps; };
static std::vector<Case> g_cases;
static std::vector<uint64_t> g_out;

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    for (size_t k = 1; k < f.size(); ++k) c.strs.push_back(tcb::unescape(f[k]));
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t i) { g_out.assign(g_cases[i].strs.size(), 0); }

static uint64_t exec(size_t i) {
  const Case& c = g_cases[i];
  uint64_t sum = 0;
  for (size_t k = 0; k < c.strs.size(); ++k) {
    const std::string& s = c.strs[k];
    Rec r;
    const char* b = s.data();
    const char* e = b + s.size();
    const char* p = b;
    try {
      p = parse_chrono_format(b, e, r);
      r.mix(1);
    } catch (const format_error& ex) {
      r.mix(2);
      for (const char* q = ex.what(); *q; ++q) r.mix(static_cast<unsigned char>(*q));
    }
    r.mix(static_cast<uint64_t>(p - b));
    g_out[k] = r.acc;
    sum += r.acc;
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  for (size_t k = 0; k < g_out.size(); ++k) h.u64(g_out[k]);
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
