// Time Capsulo bench driver for `fixed_handler::on_digit`. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with -O2 -std=c++11 -DFMT_HEADER_ONLY against /w/include.
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

// One call of on_digit on a handler whose buffer already holds some digits.
struct Item {
  std::string prefix;
  int precision;
  char digit;
  uint64_t divisor, remainder, error;
  bool integral;
};
struct Case { std::vector<Item> items; int reps; };
static std::vector<Case> g_cases;

struct Out { int result; int size; char buf[40]; };
static std::vector<Out> g_out;

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    for (size_t k = 1; k < f.size(); ++k) {
      // prefix,precision,digit,divisor,remainder,error,integral
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
      it.prefix = v[0];
      it.precision = atoi(v[1].c_str());
      it.digit = v[2][0];
      it.divisor = strtoull(v[3].c_str(), 0, 10);
      it.remainder = strtoull(v[4].c_str(), 0, 10);
      it.error = strtoull(v[5].c_str(), 0, 10);
      it.integral = v[6] == "1";
      c.items.push_back(it);
    }
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static std::vector<Out> g_state;   // buffers prepared outside the timed region
static void reset(size_t i) {
  const Case& c = g_cases[i];
  g_state.assign(c.items.size(), Out());
  for (size_t k = 0; k < c.items.size(); ++k) {
    std::memset(g_state[k].buf, 0, sizeof g_state[k].buf);
    std::memcpy(g_state[k].buf, c.items[k].prefix.data(), c.items[k].prefix.size());
    g_state[k].size = static_cast<int>(c.items[k].prefix.size());
  }
  g_out.assign(c.items.size(), Out());
}

static uint64_t exec(size_t i) {
  const Case& c = g_cases[i];
  uint64_t sum = 0;
  for (size_t k = 0; k < c.items.size(); ++k) {
    const Item& it = c.items[k];
    Out& o = g_state[k];
    fixed_handler h = {o.buf, o.size, it.precision, 0, true};
    o.result = h.on_digit(it.digit, it.divisor, it.remainder, it.error, 0, it.integral);
    o.size = h.size;
    sum += static_cast<uint64_t>(o.result) * 31 + static_cast<uint64_t>(o.size) + static_cast<unsigned char>(o.buf[0]);
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  for (size_t k = 0; k < g_state.size(); ++k) {
    h.u64(static_cast<uint64_t>(g_state[k].result));
    h.u64(static_cast<uint64_t>(g_state[k].size));
    h.add(g_state[k].buf, sizeof g_state[k].buf);
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
