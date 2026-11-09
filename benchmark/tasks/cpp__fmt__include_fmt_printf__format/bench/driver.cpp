// Time Capsulo bench driver for `basic_printf_context::format`. argv: <size> <repeat> <mode>   (mode = check | time)
// The member is reached through the library entry point internal::printf(buffer, format, args), which only constructs the context and calls format().
// Compiled with -O2 -std=c++11 -DFMT_HEADER_ONLY against /w/include.
#include "fmt/printf.h"
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

// item = format|arg|arg...     arg = type:value   types: i u l L(long long) U(unsigned long) V(unsigned long long) c(char) a(signed char)
//   h(short) H(unsigned short) b(bool) d(double) s(string) n(null C string) p(void*; value 0 = null) w(long double)
struct Arg { char type; std::string text; };
struct Item { std::string format; std::vector<Arg> args; };
struct Case { std::vector<Item> items; int reps; };
static std::vector<Case> g_cases;

static std::vector<std::string> g_res;   // output text, or "E:" + message
static memory_buffer g_buf;

static void prepare(const std::vector<std::string>& lines) {
  for (size_t i = 0; i < lines.size(); ++i) {
    std::vector<std::string> f = tcb::split_tabs(lines[i]);
    Case c;
    c.reps = atoi(f[0].c_str());
    for (size_t k = 1; k < f.size(); ++k) {
      Item it;
      std::string s = tcb::unescape(f[k]);
      size_t pos = 0;
      bool first = true;
      for (;;) {
        size_t bar = s.find('|', pos);
        std::string part = s.substr(pos, bar == std::string::npos ? std::string::npos : bar - pos);
        if (first) { it.format = part; first = false; }
        else if (!part.empty()) { Arg a; a.type = part[0]; a.text = part.substr(2); it.args.push_back(a); }
        if (bar == std::string::npos) break;
        pos = bar + 1;
      }
      c.items.push_back(it);
    }
    g_cases.push_back(c);
  }
}
static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t i) { g_res.assign(g_cases[i].items.size(), std::string()); }

static long long toll(const std::string& s) { return strtoll(s.c_str(), 0, 10); }
static unsigned long long toull(const std::string& s) { return strtoull(s.c_str(), 0, 10); }
static char g_dummy;

static uint64_t exec(size_t ci) {
  const Case& c = g_cases[ci];
  uint64_t sum = 0;
  for (size_t k = 0; k < c.items.size(); ++k) {
    const Item& it = c.items[k];
    typedef printf_context ctx;
    basic_format_arg<ctx> arr[24];
    size_t n = it.args.size();
    for (size_t a = 0; a < n && a < 24; ++a) {
      const Arg& g = it.args[a];
      switch (g.type) {
      case 'i': arr[a] = internal::make_arg<ctx>(static_cast<int>(toll(g.text))); break;
      case 'u': arr[a] = internal::make_arg<ctx>(static_cast<unsigned>(toull(g.text))); break;
      case 'l': arr[a] = internal::make_arg<ctx>(static_cast<long>(toll(g.text))); break;
      case 'L': arr[a] = internal::make_arg<ctx>(static_cast<long long>(toll(g.text))); break;
      case 'U': arr[a] = internal::make_arg<ctx>(static_cast<unsigned long>(toull(g.text))); break;
      case 'V': arr[a] = internal::make_arg<ctx>(static_cast<unsigned long long>(toull(g.text))); break;
      case 'c': arr[a] = internal::make_arg<ctx>(g.text[0]); break;
      case 'a': arr[a] = internal::make_arg<ctx>(static_cast<signed char>(toll(g.text))); break;
      case 'h': arr[a] = internal::make_arg<ctx>(static_cast<short>(toll(g.text))); break;
      case 'H': arr[a] = internal::make_arg<ctx>(static_cast<unsigned short>(toull(g.text))); break;
      case 'b': arr[a] = internal::make_arg<ctx>(g.text == "1"); break;
      case 'd': arr[a] = internal::make_arg<ctx>(strtod(g.text.c_str(), 0)); break;
      case 'w': arr[a] = internal::make_arg<ctx>(strtold(g.text.c_str(), 0)); break;
      case 's': arr[a] = internal::make_arg<ctx>(g.text.c_str()); break;
      case 'n': arr[a] = internal::make_arg<ctx>(static_cast<const char*>(0)); break;
      case 'p': arr[a] = internal::make_arg<ctx>(g.text == "0" ? static_cast<const void*>(0) : static_cast<const void*>(&g_dummy)); break;
      }
    }
    printf_args args(arr, static_cast<int>(n));
    g_buf.clear();
    try {
      internal::printf(g_buf, string_view(it.format.data(), it.format.size()), args);
      g_res[k].assign(g_buf.data(), g_buf.size());
    } catch (const format_error& e) {
      g_res[k] = std::string("E:") + e.what();
    }
    sum += g_res[k].size();
  }
  return sum;
}

static void digest(size_t, tcb::Hash& h) {
  for (size_t k = 0; k < g_res.size(); ++k) h.str(g_res[k]);
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
