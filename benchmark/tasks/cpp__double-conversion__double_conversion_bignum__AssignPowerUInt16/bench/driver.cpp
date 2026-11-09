// Time Capsulo bench driver. argv: <size> <repeat> <mode>   (mode = check | time)
// Compiled with g++ -O2 -std=c++11 -DNDEBUG -I/w, together with the other library sources.
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <stdint.h>

namespace tcb
{
	struct Rng
	{
		uint64_t s;
		explicit Rng(uint64_t seed): s(seed) {}
		uint64_t next()
		{
			s += 0x9E3779B97F4A7C15ULL;
			uint64_t z = s;
			z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
			z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
			return z ^ (z >> 31);
		}
		uint64_t below(uint64_t n) { return n ? next() % n : 0; }
		int range(int lo, int hi) { return lo + static_cast<int>(below(static_cast<uint64_t>(hi - lo + 1))); }
	};

	struct Hash
	{
		uint64_t h;
		Hash(): h(1469598103934665603ULL) {}
		void add(const void* p, size_t n)
		{
			const unsigned char* c = static_cast<const unsigned char*>(p);
			for (size_t i = 0; i < n; ++i) { h ^= c[i]; h *= 1099511628211ULL; }
		}
		void u64(uint64_t v) { add(&v, 8); }
		void str(const char* s, size_t n) { u64(n); add(s, n); }
		std::string hex() const { char b[32]; snprintf(b, sizeof b, "%016llx", static_cast<unsigned long long>(h)); return b; }
	};

	inline std::vector<std::string> split_tabs(const std::string& line)
	{
		std::vector<std::string> out;
		size_t pos = 0;
		for (;;)
		{
			size_t t = line.find('\t', pos);
			if (t == std::string::npos) { out.push_back(line.substr(pos)); break; }
			out.push_back(line.substr(pos, t - pos));
			pos = t + 1;
		}
		return out;
	}

	inline std::vector<std::string> load_lines(const char* size)
	{
		const char* task = getenv("TC_TASK");
		std::string path = std::string(task ? task : "/task") + "/bench/workload_" + size + ".txt";
		std::ifstream in(path.c_str(), std::ios::binary);
		if (!in) { fprintf(stderr, "cannot open %s\n", path.c_str()); exit(2); }
		std::vector<std::string> lines;
		std::string line;
		while (std::getline(in, line)) if (!line.empty()) lines.push_back(line);
		return lines;
	}
}

#include "double-conversion/bignum.cc"
using namespace double_conversion;

// Workload lines (tab separated): <reps> then pairs "base exponent" (space separated) in a single field.
struct Case { int reps; std::vector<unsigned> base; std::vector<int> exp; };
static std::vector<Case> g_cases;
static Bignum g_x, g_one;

static void prepare(const std::vector<std::string>& lines)
{
	g_one.AssignUInt16(1);
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[0].c_str());
		const char* p = f[1].c_str();
		char* e;
		for (;;)
		{
			unsigned long b = strtoul(p, &e, 10);
			if (e == p) break;
			p = e;
			long x = strtol(p, &e, 10);
			p = e;
			c.base.push_back(static_cast<unsigned>(b));
			c.exp.push_back(static_cast<int>(x));
		}
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t) { g_x.AssignUInt64(0x0123456789abcdefULL); }

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	uint64_t s = 0;
	for (size_t k = 0; k < c.base.size(); ++k)
	{
		g_x.AssignPowerUInt16(static_cast<uint16_t>(c.base[k]), c.exp[k]);
		s += static_cast<uint64_t>(Bignum::Compare(g_x, g_one) + 2);
	}
	return s;
}

static void digest(size_t i, tcb::Hash& h)
{
	const Case& c = g_cases[i];
	static char buf[2048];
	for (size_t k = 0; k < c.base.size(); ++k)
	{
		g_x.AssignUInt64(0x0123456789abcdefULL);
		g_x.AssignPowerUInt16(static_cast<uint16_t>(c.base[k]), c.exp[k]);
		if (!g_x.ToHexString(buf, sizeof buf)) { fprintf(stderr, "ToHexString failed\n"); exit(3); }
		h.str(buf, strlen(buf));
	}
}

// hooks provided above: prepare(lines), ncases(), reps(i), reset(i) [untimed], exec(i) [timed, returns checksum], digest(i, h)
int main(int argc, char** argv)
{
	if (argc < 4) { fprintf(stderr, "usage: driver <size> <repeat> <mode>\n"); return 2; }
	const char* size = argv[1];
	int repeat = atoi(argv[2]);
	std::string mode = argv[3];

	prepare(tcb::load_lines(size));
	size_t n = ncases();

	if (mode == "check")
	{
		tcb::Hash h;
		for (size_t i = 0; i < n; ++i)
		{
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
			for (int k = 0, kr = reps(i); k < kr; ++k)
			{
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
