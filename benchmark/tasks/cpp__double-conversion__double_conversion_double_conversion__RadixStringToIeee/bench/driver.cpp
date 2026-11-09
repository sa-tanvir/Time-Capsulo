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
//   L <reps> <radix_log2> <sign> <sep> <hexfloat> <junk> <double> <wide> <string>   (string with \t \n \\ escapes)
//   G <reps> <seed> <n> <nd> <pad>   n inputs built by the driver; <nd> caps the number of significant digits,
//                                    <pad> caps leading zeros / trailing space runs / zero tails / exponent leading zeros
// The junk value is always 777.0.
struct Item { std::string s; std::vector<uint16_t> w; int rl; bool sign, hf, junk, dbl, wide; uc16 sep; };
struct Out { uint64_t bits; int consumed; bool isjunk; };
struct Case { int reps; std::vector<Item> items; std::vector<Out> res; };
static std::vector<Case> g_cases;

static std::string unescape(const std::string& in)
{
	std::string o;
	for (size_t i = 0; i < in.size(); ++i)
	{
		if (in[i] == '\\' && i + 1 < in.size()) { char c = in[++i]; o += c == 't' ? '\t' : c == 'n' ? '\n' : c == 'r' ? '\r' : c; }
		else o += in[i];
	}
	return o;
}

static void finish(Item& it)
{
	if (it.wide) { it.w.assign(it.s.begin(), it.s.end()); it.w.push_back(0); }
}

static const char* kDig = "0123456789abcdefghijklmnopqrstuv";

static std::string digs(tcb::Rng& r, int n, int base, char sep, bool upper, int zero_pct)
{
	std::string s;
	for (int i = 0; i < n; ++i)
	{
		int d = static_cast<int>(r.below(100)) < zero_pct ? 0 : static_cast<int>(r.below(base));
		char c = kDig[d];
		if (upper && c >= 'a') c = static_cast<char>(c - 32);
		if (i > 0 && sep && r.below(7) == 0) s += sep;
		s += c;
	}
	return s;
}

static std::string bits_to_digits(const std::string& bits, int rl, bool upper)
{
	std::string b = bits;
	while (b.size() % rl) b += '0';
	std::string s;
	for (size_t i = 0; i < b.size(); i += rl)
	{
		int d = 0;
		for (int j = 0; j < rl; ++j) d = d * 2 + (b[i + j] - '0');
		char c = kDig[d];
		if (upper && c >= 'a') c = static_cast<char>(c - 32);
		s += c;
	}
	return s;
}

static Item build(tcb::Rng& r, int nd, int pad)
{
	Item it;
	it.rl = r.range(1, 5);
	int base = 1 << it.rl;
	it.sign = r.below(3) == 0;
	it.junk = r.below(3) == 0;
	it.dbl = r.below(4) != 0;
	it.wide = r.below(4) == 0;
	it.sep = r.below(4) == 0 ? '_' : 0;
	bool upper = r.below(3) == 0;
	it.hf = it.rl == 4 && r.below(3) == 0;
	std::string lead = r.below(3) == 0 ? std::string(1 + r.below(pad), '0') : std::string();
	std::string body;
	int kind = static_cast<int>(r.below(10));
	if (it.hf)
	{
		int ni = r.below(4) == 0 ? 0 : 1 + static_cast<int>(r.below(nd));
		int nf = r.below(3) == 0 ? 0 : 1 + static_cast<int>(r.below(nd));
		bool dot = r.below(2) != 0 || (ni == 0 && nf > 0);
		if (!dot) nf = 0;
		if (ni + nf == 0) ni = 1;
		if (ni == 0 && !lead.empty()) lead.clear();
		std::string m = digs(r, ni, 16, it.sep, upper, 10);
		if (dot)
		{
			m += '.';
			m += digs(r, nf, 16, it.sep, upper, 10);
			if (r.below(4) == 0) m += std::string(1 + r.below(pad), '0');       // long zero tail in the fraction
		}
		char sg = r.below(3) == 0 ? '+' : (r.below(2) ? '-' : 0);
		int ev = r.below(40) == 0 ? 99999 : static_cast<int>(r.below(1801)) - 900;
		if (ev == 99999) sg = '+';
		else if (ev < 0) { sg = '-'; ev = -ev; }
		else if (sg == '-') ev = -ev, sg = '-', ev = -ev;
		char eb[16]; snprintf(eb, sizeof eb, "%d", ev);
		std::string ex = (r.below(4) == 0 ? std::string(1 + r.below(pad), '0') : std::string()) + eb;
		body = m + (upper ? "P" : "p") + (sg ? std::string(1, sg) : std::string()) + ex;
		if (!it.junk && kind % 2) body += std::string(1 + r.below(pad), ' ');
		else if (it.junk && kind % 2) body += "zz";
		it.s = lead + body;
		finish(it);
		return it;
	}
	int nbits = it.dbl ? 53 : 24;
	switch (kind)
	{
	case 0: case 1: body = digs(r, 1 + static_cast<int>(r.below(nd)), base, it.sep, upper, 5); break;
	case 2: body = std::string(1 + r.below(pad + 1), '0'); break;                                    // zeros only
	case 3: case 4:                                                                                  // halfway / near halfway cases
	{
		std::string b = "1";
		for (int j = 1; j < nbits + static_cast<int>(r.below(4)); ++j) b += r.below(2) ? '1' : '0';
		b += '1';
		b += std::string(r.below(pad + 1) % 40, '0');
		if (kind == 4) b += '1';
		body = bits_to_digits(b, it.rl, upper);
		break;
	}
	case 5: body = digs(r, 1 + static_cast<int>(r.below(nd)), base, it.sep, upper, 5) + std::string(1 + r.below(pad), ' '); break;
	case 6: body = digs(r, 1 + static_cast<int>(r.below(nd)), base, it.sep, upper, 5) + "zz"; break;
	case 7: { body = digs(r, 2 + static_cast<int>(r.below(nd)), base, it.sep, upper, 5); body.insert(1 + r.below(body.size() - 1), "z"); break; }
	case 8:                                                                                          // 1 followed by many zeros and a late non-zero digit
	{
		body = "1" + std::string(nbits / it.rl + 1 + r.below(30), '0');
		if (r.below(2)) body += "1";
		break;
	}
	default: body = digs(r, 1 + static_cast<int>(r.below(nd)), base, it.sep, upper, 5) + " " + digs(r, 1, base, 0, false, 0); break;
	}
	it.s = lead + body;
	finish(it);
	return it;
}

template <int K, class It>
static Out run(It begin, It end, const Item& it)
{
	It cur = begin;
	bool isjunk = false;
	double v = RadixStringToIeee<K>(&cur, end, it.sign, it.sep, it.hf, it.junk, 777.0, it.dbl, &isjunk);
	Out o; memcpy(&o.bits, &v, 8); o.consumed = static_cast<int>(cur - begin); o.isjunk = isjunk;
	return o;
}

template <class It>
static Out dispatch(It begin, It end, const Item& it)
{
	switch (it.rl)
	{
	case 1: return run<1>(begin, end, it);
	case 2: return run<2>(begin, end, it);
	case 3: return run<3>(begin, end, it);
	case 4: return run<4>(begin, end, it);
	default: return run<5>(begin, end, it);
	}
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
			it.rl = atoi(f[2].c_str()); it.sign = atoi(f[3].c_str()) != 0; it.sep = static_cast<uc16>(atoi(f[4].c_str()));
			it.hf = atoi(f[5].c_str()) != 0; it.junk = atoi(f[6].c_str()) != 0; it.dbl = atoi(f[7].c_str()) != 0; it.wide = atoi(f[8].c_str()) != 0;
			it.s = unescape(f[9]);
			finish(it);
			c.items.push_back(it);
		}
		else
		{
			tcb::Rng r(strtoull(f[2].c_str(), 0, 10));
			int n = atoi(f[3].c_str()), nd = atoi(f[4].c_str()), pad = atoi(f[5].c_str());
			for (int k = 0; k < n; ++k) c.items.push_back(build(r, nd, pad));
		}
		for (size_t k = 0; k < c.items.size(); ++k)
		{
			const Item& it = c.items[k];
			if (it.s.empty()) { fprintf(stderr, "empty string\n"); exit(3); }
			if (it.hf && !IsHexFloatString(it.s.c_str(), it.s.c_str() + it.s.size(), it.sep, it.junk)) { fprintf(stderr, "invalid hex float: %s\n", it.s.c_str()); exit(3); }
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
		Out o = it.wide ? dispatch(it.w.data(), it.w.data() + it.s.size(), it) : dispatch(it.s.c_str(), it.s.c_str() + it.s.size(), it);
		c.res[k] = o;
		s += o.bits ^ static_cast<uint64_t>(o.consumed);
	}
	return s;
}

static void digest(size_t i, tcb::Hash& h)
{
	for (size_t k = 0; k < g_cases[i].items.size(); ++k)
	{
		const Out& o = g_cases[i].res[k];
		double v; memcpy(&v, &o.bits, 8);
		h.u64(v != v ? 0x7ff8000000000000ULL : o.bits);   // all NaNs equal
		h.u64(static_cast<uint64_t>(o.consumed)); h.u64(o.isjunk);
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
