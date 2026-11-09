// Time Capsulo bench driver for `grisu_gen_digits`. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with -O2 -std=c++11 -DFMT_HEADER_ONLY against /w/include. The inputs (scaled fp value, error, handler) are prepared exactly as format_float does, outside the timed region.
#include "fmt/format.h"
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

// item = mode,value,precision   mode 0: fixed number of digits (fixed_handler), mode 1: shortest (grisu_shortest_handler)
struct Item { int mode; double v; int precision; };
struct Case { std::vector<Item> items; int reps; };
static std::vector<Case> g_cases;

struct State {
  int mode;
  fp value;
  uint64_t error;
  char buf[40];
  fixed_handler fh;
  grisu_shortest_handler sh;
  int result, exp, size;
};
static std::vector<State> g_st;

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    for (size_t k = 1; k < f.size(); ++k) {
      std::vector<std::string> v;
      const std::string& s = f[k];
      size_t pos = 0;
      for (;;) {
        size_t cm = s.find(',', pos);
        if (cm == std::string::npos) { v.push_back(s.substr(pos)); break; }
        v.push_back(s.substr(pos, cm - pos));
        pos = cm + 1;
      }
      Item it;
      it.mode = atoi(v[0].c_str());
      it.v = strtod(v[1].c_str(), 0);
      it.precision = atoi(v[2].c_str());
      c.items.push_back(it);
    }
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i) {
  const Case& c = g_cases[i];
  g_st.assign(c.items.size(), State());
  for (size_t k = 0; k < c.items.size(); ++k) {
    const Item& it = c.items[k];
    State& s = g_st[k];
    std::memset(s.buf, 0, sizeof s.buf);
    s.mode = it.mode;
    s.result = s.exp = s.size = 0;
    const int min_exp = -60;
    int cached_exp10 = 0;
    if (it.mode == 0) {
      fp normalized = normalize(fp(it.v));
      const fp cached_pow = get_cached_power(min_exp - (normalized.e + fp::significand_size), cached_exp10);
      s.value = normalized * cached_pow;
      s.error = 1;
      s.fh.buf = s.buf; s.fh.size = 0; s.fh.precision = it.precision; s.fh.exp10 = -cached_exp10; s.fh.fixed = true;
    } else {
      fp fp_value;
      auto boundaries = fp_value.assign_with_boundaries(it.v);
      fp_value = normalize(fp_value);
      const fp cached_pow = get_cached_power(min_exp - (fp_value.e + fp::significand_size), cached_exp10);
      fp_value = fp_value * cached_pow;
      boundaries.lower = multiply(boundaries.lower, cached_pow.f);
      boundaries.upper = multiply(boundaries.upper, cached_pow.f);
      --boundaries.lower;
      ++boundaries.upper;
      s.sh.buf = s.buf; s.sh.size = 0; s.sh.diff = boundaries.upper - fp_value.f;
      s.value = fp(boundaries.upper, fp_value.e);
      s.error = boundaries.upper - boundaries.lower;
    }
  }
}

static uint64_t exec(size_t i) {
  size_t n = g_cases[i].items.size();
  uint64_t sum = 0;
  for (size_t k = 0; k < n; ++k) {
    State& s = g_st[k];
    int exp = 0;
    if (s.mode == 0) {
      s.result = grisu_gen_digits(s.value, s.error, exp, s.fh);
      s.size = s.fh.size;
    } else {
      s.result = grisu_gen_digits(s.value, s.error, exp, s.sh);
      s.size = s.sh.size;
    }
    s.exp = exp;
    sum += static_cast<uint64_t>(s.result) * 7 + static_cast<uint64_t>(s.exp + 400) + static_cast<unsigned char>(s.buf[0]);
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  for (size_t k = 0; k < g_st.size(); ++k) {
    const State& s = g_st[k];
    h.u64(static_cast<uint64_t>(s.result));
    h.u64(static_cast<uint64_t>(static_cast<int64_t>(s.exp)));
    h.str(s.buf, static_cast<size_t>(s.size));
  }
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
