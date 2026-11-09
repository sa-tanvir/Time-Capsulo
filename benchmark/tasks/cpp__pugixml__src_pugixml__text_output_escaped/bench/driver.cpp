// Time Capsulo bench driver for `text_output_escaped`. argv: <size> <repeat> <mode>   (mode = check | time)
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

struct CaptureWriter: xml_writer
{
	std::string out;
	virtual void write(const void* data, size_t size) { out.append(static_cast<const char*>(data), size); }
};

struct Case { std::string text; chartypex_t type; unsigned flags; int reps; };
static std::vector<Case> g_cases;
static std::string g_result;

static std::string unescape(const std::string& s)
{
	std::string o;
	for (size_t i = 0; i < s.size(); ++i)
	{
		if (s[i] == '\\' && i + 1 < s.size())
		{
			char c = s[++i];
			if (c == 'x' && i + 2 < s.size() + 0) { o.push_back(static_cast<char>(strtoul(s.substr(i + 1, 2).c_str(), 0, 16))); i += 2; }
			else o.push_back(c == 't' ? '\t' : c == 'n' ? '\n' : c == 'r' ? '\r' : c);
		}
		else o.push_back(s[i]);
	}
	return o;
}

static std::string expand(uint64_t seed, size_t len, unsigned special_pct)
{
	tcb::Rng r(seed);
	static const char plain[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:-_/()[]{}=+*!?@#$%^~`|";
	static const char special[] = "&<>\"'&<>\"'";
	std::string s;
	while (s.size() < len)
	{
		if (r.below(100) < special_pct)
		{
			uint64_t k = r.below(10);
			if (k < 7) s.push_back(special[r.below(sizeof(special) - 1)]);
			else s.push_back(static_cast<char>(1 + r.below(31)));          // control characters (tab/newline/CR included)
		}
		else if (r.below(40) == 0)
		{
			static const char* const mb[] = {"\xc3\xa9", "\xe2\x82\xac", "\xf0\x9f\x98\x80", "\xd0\x96", "\xe3\xb0\x80"};
			s += mb[r.below(5)];
		}
		else
		{
			size_t run = 1 + r.below(30);
			for (size_t i = 0; i < run; ++i) s.push_back(plain[r.below(sizeof(plain) - 1)]);
		}
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
		if (f[0] == "L")   // L reps type flags text
		{
			c.type = atoi(f[2].c_str()) ? ctx_special_attr : ctx_special_pcdata;
			c.flags = static_cast<unsigned>(atoi(f[3].c_str()));
			c.text = f.size() > 4 ? unescape(f[4]) : std::string();
		}
		else               // G reps seed type flags len special_pct
		{
			c.type = atoi(f[3].c_str()) ? ctx_special_attr : ctx_special_pcdata;
			c.flags = static_cast<unsigned>(atoi(f[4].c_str()));
			c.text = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[5].c_str())), static_cast<unsigned>(atoi(f[6].c_str())));
		}
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t) { g_result.clear(); }

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	CaptureWriter w;
	{
		xml_buffered_writer bw(w, encoding_utf8);
		text_output_escaped(bw, c.text.c_str(), c.type, c.flags);
		bw.flush();
	}
	g_result.swap(w.out);
	return g_result.size();
}

static void digest(size_t, tcb::Hash& h) { h.str(g_result); }

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
