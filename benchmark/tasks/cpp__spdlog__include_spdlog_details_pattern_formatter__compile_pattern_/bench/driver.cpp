// Time Capsulo bench driver. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with -O2 -std=c++11 -fno-access-control -DSPDLOG_ENABLE_MESSAGE_COUNTER against /w/include (header-only spdlog).
#ifndef SPDLOG_ENABLE_MESSAGE_COUNTER
#define SPDLOG_ENABLE_MESSAGE_COUNTER
#endif
#include "spdlog/spdlog.h"
#include "spdlog/details/pattern_formatter.h"
#include "spdlog/details/file_helper.h"
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

// deterministic filler text of n characters (no tab, no backslash)
inline std::string make_text(size_t n, uint64_t seed) {
  static const char A[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJ0123456789 _-.:/[]()";
  Rng r(seed);
  std::string s;
  s.reserve(n);
  for (size_t i = 0; i < n; ++i) s += A[r.below(sizeof A - 1)];
  return s;
}

// A log message description shared by the pattern-formatter tasks.
struct MsgSpec {
  long long secs; long nanos; int level;
  std::string name, payload, file, func;
  unsigned line;
  size_t tid, msg_id;
};
// fields f[k..k+8]: secs nanos level namelen payloadlen line seed tid msgid
inline MsgSpec parse_msg(const std::vector<std::string>& f, size_t k) {
  MsgSpec m;
  m.secs = atoll(f[k].c_str());
  m.nanos = atol(f[k + 1].c_str());
  m.level = atoi(f[k + 2].c_str());
  uint64_t seed = strtoull(f[k + 6].c_str(), 0, 10);
  m.name = make_text(strtoul(f[k + 3].c_str(), 0, 10), seed * 3 + 1);
  m.payload = make_text(strtoul(f[k + 4].c_str(), 0, 10), seed * 3 + 2);
  m.line = static_cast<unsigned>(atol(f[k + 5].c_str()));
  m.file = make_text(3 + seed % 9, seed * 3 + 3) + ".cpp";
  m.func = make_text(2 + seed % 7, seed * 3 + 4);
  m.tid = strtoull(f[k + 7].c_str(), 0, 10);
  m.msg_id = strtoull(f[k + 8].c_str(), 0, 10);
  return m;
}
inline spdlog::details::log_msg make_msg(const MsgSpec& m) {
  spdlog::source_loc loc = m.line ? spdlog::source_loc(m.file.c_str(), static_cast<int>(m.line), m.func.c_str()) : spdlog::source_loc();
  spdlog::details::log_msg msg(loc, &m.name, static_cast<spdlog::level::level_enum>(m.level), spdlog::string_view_t(m.payload.data(), m.payload.size()));
  msg.time = spdlog::log_clock::time_point(std::chrono::duration_cast<spdlog::log_clock::duration>(std::chrono::seconds(m.secs) + std::chrono::nanoseconds(m.nanos)));
  msg.thread_id = m.tid;
  msg.msg_id = m.msg_id;
  return msg;
}
inline void put_num(fmt::memory_buffer& out, unsigned long long v) { char b[32]; int n = snprintf(b, sizeof b, "|%llu", v); out.append(b, b + n); }
inline void put_color(fmt::memory_buffer& out, const spdlog::details::log_msg& m) { put_num(out, m.color_range_start); put_num(out, m.color_range_end); }
}  // namespace tcb

using namespace spdlog;
using namespace spdlog::details;

struct Case { tcb::MsgSpec m; std::string pattern; };
static bool parse_case(const std::vector<std::string>& f, Case& c) { c.m = tcb::parse_msg(f, 0); c.pattern = f[9]; return true; }
static pattern_formatter& pf() { static pattern_formatter x("", pattern_time_type::utc, ""); return x; }
static void check_case(const Case& c, fmt::memory_buffer& out) {
  pf().compile_pattern_(c.pattern);
  log_msg msg = tcb::make_msg(c.m);
  pf().format(msg, out);
  tcb::put_color(out, msg);
}
static void time_case(const Case& c, uint64_t& sink) {
  pf().compile_pattern_(c.pattern);
  sink += pf().formatters_.size();
}

int main(int argc, char** argv) {
  if (argc < 4) { fprintf(stderr, "usage: driver <size> <repeat> <mode>\n"); return 2; }
  const char* size = argv[1];
  long repeat = atol(argv[2]);
  std::string mode = argv[3];
  std::vector<std::string> lines = tcb::load_lines(size);
  std::vector<Case> cases;
  for (size_t i = 0; i < lines.size(); ++i) {
    Case c;
    if (!parse_case(tcb::split_tabs(lines[i]), c)) { fprintf(stderr, "bad workload line %zu\n", i); return 2; }
    cases.push_back(c);
  }
  size_t n = cases.size();
  if (mode == "check") {
    tcb::Hash h;
    fmt::memory_buffer out;
    for (size_t i = 0; i < n; ++i) {
      out.resize(0);
      check_case(cases[i], out);
      h.str(out.data(), out.size());
    }
    printf("{\"cases\": %zu, \"output_digest\": \"%s\"}\n", n, h.hex().c_str());
    return 0;
  }
  uint64_t sink = 0;
  typedef std::chrono::steady_clock clk;
  clk::time_point t0 = clk::now();
  for (long r = 0; r < repeat; ++r)
    for (size_t i = 0; i < n; ++i) time_case(cases[i], sink);
  clk::time_point t1 = clk::now();
  fprintf(stderr, "checksum %llu\n", static_cast<unsigned long long>(sink));
  printf("{\"cases\": %zu, \"repeat\": %ld, \"elapsed_s\": %.6f}\n", n, repeat, std::chrono::duration<double>(t1 - t0).count());
  return 0;
}
