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

#include "double-conversion/double-conversion.cc"
using namespace double_conversion;

// Workload lines (tab separated):
//   L <reps> <sep> <junk> <wide> <string>      sep = character code of the separator (0 = none); string with \t \n \\ escapes
//   G <reps> <seed> <n> <nd> <pad>              n strings built by the driver (hex-float-like text, valid and broken variants);
//                                               <nd> caps the digit runs, <pad> caps the length of trailing space runs / leading zeros
struct Item { std::string s; std::vector<uint16_t> w; uc16 sep; bool junk; bool wide; };
struct Case { int reps; std::vector<Item> items; std::vector<uint8_t> res; };
static std::vector<Case> g_cases;

static std::string unescape(const std::string& in)
{
	std::string o;
	for (size_t i = 0; i < in.size(); ++i)
	{
		if (in[i] == '\\' && i + 1 < in.size())
		{
			char c = in[++i];
			o += c == 't' ? '\t' : c == 'n' ? '\n' : c == 'r' ? '\r' : c;
		}
		else o += in[i];
	}
	return o;
}

static void finish(Item& it)
{
	if (it.wide) { it.w.assign(it.s.begin(), it.s.end()); it.w.push_back(0); }
}

static std::string digits(tcb::Rng& r, int n, int base, char sep, bool upper)
{
	std::string s;
	for (int i = 0; i < n; ++i)
	{
		int d = static_cast<int>(r.below(base));
		char c = d < 10 ? static_cast<char>('0' + d) : static_cast<char>((upper ? 'A' : 'a') + d - 10);
		if (i > 0 && sep && r.below(6) == 0) s += static_cast<char>(sep);
		s += c;
	}
	return s;
}

static Item build(tcb::Rng& r, int nd, int pad)
{
	Item it;
	it.junk = r.below(2) != 0;
	it.wide = r.below(4) == 0;
	it.sep = r.below(3) == 0 ? '_' : 0;
	bool upper = r.below(3) == 0;
	int kind = static_cast<int>(r.below(13));
	int ni = r.below(5) == 0 ? 0 : 1 + static_cast<int>(r.below(nd));
	int nf = r.below(3) == 0 ? 0 : 1 + static_cast<int>(r.below(nd));
	bool dot = r.below(2) != 0 || (ni == 0 && nf > 0);
	if (!dot) nf = 0;
	if (ni + nf == 0) ni = 1;
	std::string mant = digits(r, ni, 16, it.sep, upper);
	if (dot) { mant += '.'; mant += digits(r, nf, 16, it.sep, upper); }
	char sg = r.below(3) == 0 ? '+' : (r.below(2) ? '-' : 0);
	int ne = 1 + static_cast<int>(r.below(nd / 4 + 1));
	std::string ex = digits(r, ne, 10, it.sep, false);
	std::string valid = mant + (upper ? "P" : "p") + (sg ? std::string(1, sg) : std::string()) + ex;
	switch (kind)
	{
	case 0: case 1: case 2: case 3: it.s = valid; break;
	case 4: it.s = valid + std::string(1 + r.below(pad), ' '); break;
	case 5: it.s = valid + "zz"; break;
	case 6: it.s = std::string(dot ? "." : "") + "p" + ex; break;
	case 7: it.s = mant; break;
	case 8: it.s = mant + "p" + (sg ? std::string(1, sg) : std::string()) + (r.below(2) ? "x" : ""); break;
	case 9: { std::string m = mant; m.insert(m.size() / 2, "g"); it.s = m + "p" + ex; break; }
	case 10: it.s = valid + " zz"; break;
	case 11: it.s = valid + "\t\n " + std::string(r.below(pad), ' '); break;
	default: it.s = mant + "_." + digits(r, 2, 16, 0, false) + "p" + ex; break;
	}
	finish(it);
	return it;
}

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[1].c_str());
		if (f[0] == "L")
		{
			Item it;
			it.sep = static_cast<uc16>(atoi(f[2].c_str()));
			it.junk = atoi(f[3].c_str()) != 0;
			it.wide = atoi(f[4].c_str()) != 0;
			it.s = unescape(f[5]);
			finish(it);
			c.items.push_back(it);
		}
		else
		{
			tcb::Rng r(strtoull(f[2].c_str(), 0, 10));
			int n = atoi(f[3].c_str()), nd = atoi(f[4].c_str()), pad = atoi(f[5].c_str());
			for (int k = 0; k < n; ++k) c.items.push_back(build(r, nd, pad));
		}
		c.res.resize(c.items.size());
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t) {}

static uint64_t exec(size_t i)
{
	Case& c = g_cases[i];
	uint64_t s = 0;
	for (size_t k = 0; k < c.items.size(); ++k)
	{
		const Item& it = c.items[k];
		bool v;
		if (it.wide) v = IsHexFloatString(it.w.data(), it.w.data() + it.s.size(), it.sep, it.junk);
		else v = IsHexFloatString(it.s.c_str(), it.s.c_str() + it.s.size(), it.sep, it.junk);
		c.res[k] = v;
		s += v;
	}
	return s;
}

static void digest(size_t i, tcb::Hash& h)
{
	for (size_t k = 0; k < g_cases[i].items.size(); ++k) h.u64(g_cases[i].res[k]);
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
