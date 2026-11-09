// Time Capsulo bench driver for `string_to_integer`. argv: <size> <repeat> <mode>   (mode = check | time)
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

struct Case { int type; std::string s; int reps; };
static std::vector<Case> g_cases;
static uint64_t g_out[4];
static int g_ntypes;

static std::string expand(uint64_t seed, size_t len, int kind)
{
	tcb::Rng r(seed);
	std::string s;
	const char* hexd = "0123456789abcdefABCDEF";
	switch (kind)
	{
	case 0: // random decimal digits, no leading zero
		s.push_back('1' + char(r.below(9)));
		for (size_t i = 1; i < len; ++i) s.push_back('0' + char(r.below(10)));
		break;
	case 1: // hex with 0x prefix
		s = (r.below(2) ? "0x" : "0X");
		s.push_back("123456789abcdef"[r.below(15)]);
		for (size_t i = 1; i < len; ++i) s.push_back(hexd[r.below(22)]);
		break;
	case 2: // many leading zeros then a short number
	{
		s.assign(len, '0');
		size_t d = 1 + r.below(19);
		for (size_t i = 0; i < d; ++i) s.push_back((i ? '0' : '1') + char(r.below(i ? 10 : 9)));
		break;
	}
	case 3: // negative decimal
		s = "-";
		s.push_back('1' + char(r.below(9)));
		for (size_t i = 1; i < len; ++i) s.push_back('0' + char(r.below(10)));
		break;
	case 4: // negative hex with leading zeros and a short value
	{
		s = "-0x";
		s.append(len, '0');
		size_t d = 1 + r.below(16);
		for (size_t i = 0; i < d; ++i) s.push_back(hexd[(i ? 0 : 1) + r.below(i ? 22 : 15)]);
		break;
	}
	default: // whitespace prefix, optional plus, leading zeros, short number, trailing junk
	{
		const char* ws = " \t\r\n";
		for (size_t i = 0; i < len / 2; ++i) s.push_back(ws[r.below(4)]);
		if (r.below(2)) s.push_back('+');
		s.append(len / 2, '0');
		size_t d = 1 + r.below(9);
		for (size_t i = 0; i < d; ++i) s.push_back((i ? '0' : '1') + char(r.below(i ? 10 : 9)));
		s += "xyz";
		break;
	}
	}
	return s;
}

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

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		if (f[0] == "L")
		{
			c.reps = atoi(f[1].c_str());
			c.type = atoi(f[2].c_str());
			c.s = f.size() > 3 ? unescape(f[3]) : std::string();
		}
		else
		{
			c.reps = atoi(f[1].c_str());
			uint64_t seed = strtoull(f[2].c_str(), 0, 10);
			c.type = atoi(f[3].c_str());
			c.s = expand(seed, static_cast<size_t>(atol(f[4].c_str())), atoi(f[5].c_str()));
		}
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t) {}

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	const char_t* v = c.s.c_str();
	uint64_t sum = 0;
	g_ntypes = 0;
	for (int t = 0; t < 4; ++t)
	{
		if (c.type != 4 && c.type != t) continue;
		uint64_t r = 0;
		if (t == 0) r = string_to_integer<unsigned int>(v, static_cast<unsigned int>(INT_MIN), INT_MAX);
		else if (t == 1) r = string_to_integer<unsigned int>(v, 0, UINT_MAX);
		else if (t == 2) r = string_to_integer<unsigned long long>(v, static_cast<unsigned long long>(LLONG_MIN), LLONG_MAX);
		else r = string_to_integer<unsigned long long>(v, 0, ULLONG_MAX);
		g_out[g_ntypes++] = r;
		sum += r;
	}
	return sum;
}

static void digest(size_t, tcb::Hash& h)
{
	h.u64(g_ntypes);
	for (int k = 0; k < g_ntypes; ++k) h.u64(g_out[k]);
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
