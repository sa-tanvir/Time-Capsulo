// Time Capsulo bench driver for `unique`. argv: <size> <repeat> <mode>   (mode = check | time)
// Includes the library source directly (so file-local functions are reachable); compiled with -O2 -std=c++11.
#include "pugixml.cpp"

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
		uint64_t below(uint64_t n) { return next() % n; }
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
		void str(const std::string& s) { u64(s.size()); add(s.data(), s.size()); }
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

using namespace pugi;
using namespace pugi::impl;

struct Pair { int a; int b; };
static bool operator==(const Pair& x, const Pair& y) { return x.a == y.a && x.b == y.b; }
static bool operator!=(const Pair& x, const Pair& y) { return !(x == y); }

// type 0: int, type 1: Pair (equality needs both fields)
struct Case { int type; std::vector<int> v; int reps; };
static std::vector<Case> g_cases;
static std::vector<int> g_ints;
static std::vector<Pair> g_pairs;
static size_t g_kept;

// groups of equal values: run length drawn from 1..maxrun (maxrun 1 = all distinct); mode 3: one single run; mode 4: a duplicate pair at the very end
static std::vector<int> expand(uint64_t seed, size_t n, unsigned maxrun, int mode)
{
	tcb::Rng r(seed);
	std::vector<int> v;
	v.reserve(n);
	int value = -static_cast<int>(r.below(1000));
	if (mode == 3) { v.assign(n, value); return v; }
	while (v.size() < n)
	{
		size_t run = 1 + r.below(maxrun);
		if (mode == 2 && v.empty()) run = 1 + r.below(maxrun * 4);   // long head run
		for (size_t k = 0; k < run && v.size() < n; ++k) v.push_back(value);
		value += 1 + static_cast<int>(r.below(5));
	}
	if (mode == 4 && n >= 2) v[n - 1] = v[n - 2];
	return v;
}

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[1].c_str());
		if (f[0] == "L")   // L reps type v1,v2,...
		{
			c.type = atoi(f[2].c_str());
			const std::string& l = f.size() > 3 ? f[3] : std::string();
			size_t pos = 0;
			while (pos < l.size())
			{
				size_t comma = l.find(',', pos);
				if (comma == std::string::npos) comma = l.size();
				c.v.push_back(atoi(l.substr(pos, comma - pos).c_str()));
				pos = comma + 1;
			}
		}
		else               // G reps seed type n maxrun mode
		{
			c.type = atoi(f[3].c_str());
			c.v = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[4].c_str())), static_cast<unsigned>(atoi(f[5].c_str())), atoi(f[6].c_str()));
		}
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i)
{
	const Case& c = g_cases[i];
	if (c.type == 1)
	{
		g_pairs.resize(c.v.size());
		for (size_t k = 0; k < c.v.size(); ++k) { g_pairs[k].a = c.v[k]; g_pairs[k].b = c.v[k] * 3 + 1; }
	}
	else g_ints = c.v;
}

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	size_t n = c.v.size();
	if (c.type == 1)
	{
		Pair* b = g_pairs.empty() ? 0 : &g_pairs[0];
		Pair* e = pugi::impl::unique(b, b + n);
		g_kept = static_cast<size_t>(e - b);
	}
	else
	{
		int* b = g_ints.empty() ? 0 : &g_ints[0];
		int* e = pugi::impl::unique(b, b + n);
		g_kept = static_cast<size_t>(e - b);
	}
	return g_kept;
}

static void digest(size_t i, tcb::Hash& h)
{
	h.u64(g_kept);
	if (g_cases[i].type == 1) { for (size_t k = 0; k < g_kept; ++k) { h.u64(static_cast<uint32_t>(g_pairs[k].a)); h.u64(static_cast<uint32_t>(g_pairs[k].b)); } }
	else { for (size_t k = 0; k < g_kept; ++k) h.u64(static_cast<uint32_t>(g_ints[k])); }
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
