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

#include "double-conversion/fast-dtoa.cc"
using namespace double_conversion;

// Workload lines (tab separated): <reps> <seed> <n> <bits>
struct Item { uint64_t rest, tk, unit; int len, kappa; char dig[20]; };
struct Case { int reps; std::vector<Item> items; };
static std::vector<Case> g_cases;
static char* g_buf; static uint8_t* g_ret; static int* g_kappa;
static const int kSlot = 24;

static int bitlen(uint64_t v) { int b = 0; while (v) { ++b; v >>= 1; } return b; }

static void prepare(const std::vector<std::string>& lines)
{
	size_t maxn = 0;
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[0].c_str());
		tcb::Rng r(strtoull(f[1].c_str(), 0, 10));
		int n = atoi(f[2].c_str()), B = atoi(f[3].c_str());
		for (int k = 0; k < n; ++k)
		{
			Item it;
			uint64_t tk = 1;
			int j = r.range(0, 18);
			for (int q = 0; q < j; ++q) tk *= 10;
			while (bitlen(tk) > B) tk /= 10;
			int room = B - bitlen(tk);
			if (room > 0 && r.below(2)) tk <<= r.range(0, room);
			it.tk = tk;
			switch (r.below(5))
			{
			case 0: it.unit = 1 + r.below(4); break;
			case 1: it.unit = r.below(tk + tk / 2 + 1); break;       // may be >= ten_kappa
			default: it.unit = 1 + r.below(tk / (1 + r.below(8)) + 1);
			}
			switch (r.below(4))
			{
			case 0: it.rest = r.below(tk / 2 + 1); break;
			case 1: it.rest = tk - 1 - r.below(tk / 4 + 1); break;
			default: it.rest = r.below(tk);
			}
			if (it.rest >= tk) it.rest = tk - 1;
			it.len = r.range(1, 17);
			int p9 = r.below(3) == 0 ? 10 : 6;
			for (int q = 0; q < it.len; ++q) it.dig[q] = static_cast<char>('0' + (static_cast<int>(r.below(10)) < p9 ? 9 : r.below(10)));
			it.kappa = r.range(-20, 20);
			c.items.push_back(it);
		}
		if (c.items.size() > maxn) maxn = c.items.size();
		g_cases.push_back(c);
	}
	g_buf = new char[maxn * kSlot]; g_ret = new uint8_t[maxn]; g_kappa = new int[maxn];
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i)
{
	const Case& c = g_cases[i];
	for (size_t k = 0; k < c.items.size(); ++k) { memcpy(g_buf + k * kSlot, c.items[k].dig, c.items[k].len); g_kappa[k] = c.items[k].kappa; }
}

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	uint64_t s = 0;
	for (size_t k = 0; k < c.items.size(); ++k)
	{
		const Item& it = c.items[k];
		bool ok = RoundWeedCounted(Vector<char>(g_buf + k * kSlot, kSlot), it.len, it.rest, it.tk, it.unit, &g_kappa[k]);
		g_ret[k] = ok;
		s += ok + static_cast<uint64_t>(g_kappa[k] + 100);
	}
	return s;
}

static void digest(size_t i, tcb::Hash& h)
{
	const Case& c = g_cases[i];
	for (size_t k = 0; k < c.items.size(); ++k) { h.u64(g_ret[k]); h.u64(static_cast<uint64_t>(g_kappa[k] + 1000)); h.str(g_buf + k * kSlot, c.items[k].len); }
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
