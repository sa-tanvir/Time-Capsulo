// Time Capsulo bench driver for `strconv_escape`. argv: <size> <repeat> <mode>   (mode = check | time)
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

struct Case { std::string text; int reps; };
static std::vector<Case> g_cases;
static std::vector<char> g_buf;
static size_t g_result_len;

static std::string unescape(const std::string& s)
{
	std::string o;
	for (size_t i = 0; i < s.size(); ++i)
	{
		if (s[i] == '\\' && i + 1 < s.size())
		{
			char c = s[++i];
			o.push_back(c == 't' ? '\t' : c == 'n' ? '\n' : c == 'r' ? '\r' : c);
		}
		else o.push_back(s[i]);
	}
	return o;
}

static std::string expand(uint64_t seed, size_t ntokens, unsigned invalid_pct)
{
	static const char* const invalid[] = {"&#;", "&#x;", "&;", "&#x-;", "&#-;", "&#1", "&#x1", "&#1-", "&q", "&qu", "&quo", "&quot", "&a", "&am",
		"&amp", "&ap", "&apo", "&apos", "&l", "&lt", "&g", "&gt", "&#X41;", "&#xg;", "&#a;", "&#12a;", "&xyz;", "&", "&&amp;", "&#1&#2;", "&#x4G;", "&am&gt;"};
	static const char* const named[] = {"&amp;", "&lt;", "&gt;", "&quot;", "&apos;"};
	tcb::Rng r(seed);
	std::string s;
	char buf[40];
	for (size_t i = 0; i < ntokens; ++i)
	{
		size_t plain = r.below(6);
		for (size_t k = 0; k < plain; ++k) s.push_back("abc xyz;#<>"[r.below(11)]);
		if (r.below(100) < invalid_pct)
		{
			s += invalid[r.below(sizeof(invalid) / sizeof(invalid[0]))];
			continue;
		}
		uint64_t kind = r.below(10);
		if (kind < 4) { s += named[r.below(5)]; continue; }
		uint64_t cls = r.below(20), v;
		if (cls < 8) v = 1 + r.below(127);
		else if (cls < 12) v = 128 + r.below(0x800 - 128);
		else if (cls < 16) v = 0x800 + r.below(0x10000 - 0x800);
		else if (cls < 19) v = 0x10000 + r.below(0x110000 - 0x10000);
		else v = 0x110000 + r.below(0xFFFFFFFFULL - 0x110000);
		if (kind < 7) snprintf(buf, sizeof buf, "&#%llu;", static_cast<unsigned long long>(v));
		else if (kind < 9) snprintf(buf, sizeof buf, "&#x%llx;", static_cast<unsigned long long>(v));
		else snprintf(buf, sizeof buf, "&#x%llX;", static_cast<unsigned long long>(v));
		s += buf;
	}
	return s;
}

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[1].c_str());
		if (f[0] == "L") c.text = f.size() > 2 ? unescape(f[2]) : std::string();
		else c.text = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[3].c_str())), static_cast<unsigned>(atoi(f[4].c_str())));
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i)
{
	const std::string& t = g_cases[i].text;
	g_buf.assign(t.begin(), t.end());
	g_buf.push_back(0);
	g_buf.push_back(0);
}

// Walks the text like the pcdata parser does: every '&' goes through strconv_escape, the gap is flushed at the end.
static uint64_t exec(size_t)
{
	char_t* base = &g_buf[0];
	char_t* s = base;
	gap g;
	uint64_t sum = 0;
	while (*s)
	{
		if (*s == '&')
		{
			char_t* e = strconv_escape(s, g);
			sum = sum * 31 + static_cast<uint64_t>(e - s);
			s = e;
		}
		else ++s;
	}
	char_t* end = g.flush(s);
	*end = 0;
	g_result_len = static_cast<size_t>(end - base);
	return sum + g_result_len;
}

static void digest(size_t, tcb::Hash& h)
{
	h.u64(g_result_len);
	h.add(&g_buf[0], g_result_len);
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
