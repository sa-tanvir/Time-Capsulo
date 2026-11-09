// Time Capsulo bench driver for `parse_declaration_encoding`. argv: <size> <repeat> <mode>   (mode = check | time)
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
static std::vector<uint8_t> g_in;
static bool g_ok;
static int64_t g_off;
static uint64_t g_len;

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

static std::string padding(tcb::Rng& r, size_t len, bool allow_e)
{
	// printable filler without '?' and without the letter n, so that it cannot contain "en" or the declaration end
	static const char alpha[] = "abcd fghijklm\topq\nrstuvwxyz0123456789 .-_:\x80\xe9";
	std::string p;
	for (size_t i = 0; i < len; ++i)
	{
		char c = alpha[r.below(sizeof(alpha) - 1)];
		if (c == 'e' && !allow_e) c = 'a';
		p.push_back(c);
	}
	return p;
}

static std::string expand(uint64_t seed, size_t len, int kind)
{
	tcb::Rng r(seed);
	static const char* const names[] = {"UTF-8", "utf-16", "ISO-8859-1", "latin1", "windows-1252", "x_y:z.1", "", "A"};
	std::string name = names[r.below(8)];
	std::string q(1, r.below(2) ? '"' : '\'');
	std::string s = "<?xml version=" + q + "1.0" + q;
	s += (r.below(2) ? " " : "\r\n\t");
	s += padding(r, len, true);
	switch (kind)
	{
	case 0: s += " encoding" + std::string(r.below(3), ' ') + "=" + std::string(r.below(3), ' ') + q + name + q + " standalone='yes'?><root/>"; break;
	case 1: s += " standalone='yes'?><root/>"; break;                                   // no encoding attribute: stops at '?'
	case 2: s += " enable=" + q + "x" + q + "?>"; break;                              // "en" that is not "encoding"
	case 3: s += " encoding=" + q + name; break;                                       // unterminated value
	case 4: s += " encoding" + std::string(r.below(3), ' ') + q + name + q; break;     // missing '='
	default: s += " encoding=" + name + q; break;                                      // missing opening delimiter
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
		else c.text = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[3].c_str())), atoi(f[4].c_str()));
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i)
{
	const std::string& t = g_cases[i].text;
	g_in.assign(t.begin(), t.end());
	g_in.push_back(0);
}

static uint64_t exec(size_t i)
{
	size_t n = g_cases[i].text.size();
	const uint8_t* data = &g_in[0];
	const uint8_t* enc = 0;
	size_t enc_len = 0;
	g_ok = parse_declaration_encoding(data, n, enc, enc_len);
	g_off = g_ok ? enc - data : -1;
	g_len = g_ok ? enc_len : 0;
	return g_ok ? static_cast<uint64_t>(g_off) + g_len + 1 : 0;
}

static void digest(size_t, tcb::Hash& h)
{
	h.u64(g_ok);
	h.u64(static_cast<uint64_t>(g_off));
	h.u64(g_len);
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
