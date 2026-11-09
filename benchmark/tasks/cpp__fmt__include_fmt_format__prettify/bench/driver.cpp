// Time Capsulo bench driver for `float_writer::prettify`. argv: <size> <repeat> <mode>   (mode = check | time)
// prettify is private: the driver calls it through the public constructor (size) and operator() (output). -O2 -std=c++11 -DFMT_HEADER_ONLY.
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

struct Item {
  std::string digits;
  int exp, precision, format, sign;
  bool upper, trailing;
  char point;
};
struct Case { std::vector<Item> items; int reps; };
static std::vector<Case> g_cases;

enum { SLOT = 720 };
static std::vector<char> g_buf;       // SLOT bytes per item
static std::vector<int> g_len;        // bytes written by operator()
static std::vector<size_t> g_size;    // size() reported by the writer

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    for (size_t k = 1; k < f.size(); ++k) {
      // digits,exp,precision,format,sign,upper,trailing,point
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
      it.digits = v[0];
      it.exp = atoi(v[1].c_str());
      it.precision = atoi(v[2].c_str());
      it.format = atoi(v[3].c_str());
      it.sign = atoi(v[4].c_str());
      it.upper = v[5] == "1";
      it.trailing = v[6] == "1";
      it.point = v[7][0];
      c.items.push_back(it);
    }
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t i) {
  size_t n = g_cases[i].items.size();
  g_buf.assign(n * SLOT, 0);
  g_len.assign(n, 0);
  g_size.assign(n, 0);
}

static uint64_t exec(size_t i) {
  const Case& c = g_cases[i];
  uint64_t sum = 0;
  for (size_t k = 0; k < c.items.size(); ++k) {
    const Item& it = c.items[k];
    float_specs fs = float_specs();
    fs.precision = it.precision;
    fs.format = static_cast<float_format>(it.format);
    fs.sign = static_cast<sign_t>(it.sign);
    fs.upper = it.upper;
    fs.trailing_zeros = it.trailing;
    float_writer<char> w(it.digits.data(), static_cast<int>(it.digits.size()), it.exp, fs, it.point);
    char* base = &g_buf[k * SLOT];
    char* p = base;
    w(p);
    g_len[k] = static_cast<int>(p - base);
    g_size[k] = w.size();
    sum += g_size[k] + static_cast<unsigned char>(base[0]);
  }
  return sum;
}

static void digest(size_t i, tcb::Hash& h) {
  for (size_t k = 0; k < g_len.size(); ++k) {
    h.u64(g_size[k]);
    h.str(&g_buf[k * SLOT], static_cast<size_t>(g_len[k]));
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
