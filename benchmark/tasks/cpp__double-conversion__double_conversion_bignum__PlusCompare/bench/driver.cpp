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

// Workload lines (tab separated):
//   L <reps> <a> <b> <c>        operands "hexdigits" or "hexdigits@k" (value shifted left by k*28 bits); "0" is zero
//   G <reps> <seed> <n> <maxdigits> <maxshift>   n random triples built by the driver (see build())
struct Case { int reps; size_t n; Bignum* a; Bignum* b; Bignum* c; std::vector<int> res; };
static std::vector<Case> g_cases;

static void set_operand(Bignum& x, const std::string& hex, int shift)
{
	if (hex.empty() || hex == "0") { x.AssignUInt16(0); return; }
	x.AssignHexString(Vector<const char>(hex.c_str(), static_cast<int>(hex.size())));
	if (shift) x.ShiftLeft(shift * 28);
}

static void parse_operand(const std::string& f, Bignum& x)
{
	size_t at = f.find('@');
	std::string hex = at == std::string::npos ? f : f.substr(0, at);
	int shift = at == std::string::npos ? 0 : atoi(f.c_str() + at + 1);
	set_operand(x, hex, shift);
}

static std::string rnd_hex(tcb::Rng& r, int nd)
{
	std::string s;
	for (int i = 0; i < nd; ++i)
	{
		unsigned d = static_cast<unsigned>(r.below(16));
		if (i == 0 && d == 0) d = 1 + static_cast<unsigned>(r.below(15));
		if (r.below(9) == 0) d = r.below(2) ? 0 : 15;   // zero and f runs make carries/borrows
		if (i == 0 && d == 0) d = 1;
		s += "0123456789abcdef"[d];
	}
	return s;
}

static int rnd_len(tcb::Rng& r, int maxd)
{
	switch (r.below(8))
	{
	case 0: return 0;
	case 1: return 1 + static_cast<int>(r.below(3));
	case 2: return maxd;
	default: return 1 + static_cast<int>(r.below(maxd));
	}
}

static void build(Case& c, uint64_t seed, int n, int maxd, int maxshift)
{
	tcb::Rng r(seed);
	c.n = n;
	c.a = new Bignum[n]; c.b = new Bignum[n]; c.c = new Bignum[n];
	Bignum tmp;
	for (int k = 0; k < n; ++k)
	{
		int da = rnd_len(r, maxd), db = rnd_len(r, maxd);
		if (r.below(3) == 0 && db > da) da = db;
		int sa = r.below(3) == 0 ? static_cast<int>(r.below(maxshift + 1)) : 0;
		int sb = r.below(3) == 0 ? static_cast<int>(r.below(maxshift + 1)) : 0;
		set_operand(c.a[k], rnd_hex(r, da), sa);
		set_operand(c.b[k], rnd_hex(r, db), sb);
		Bignum& cc = c.c[k];
		int mode = static_cast<int>(r.below(12));
		cc.AssignBignum(c.a[k]);
		cc.AddBignum(c.b[k]);
		switch (mode)
		{
		case 0: case 1: case 2: break;                         // exact sum
		case 3: cc.AddUInt64(1); break;
		case 4: tmp.AssignUInt64(1); if (Bignum::Less(tmp, cc) || Bignum::Equal(tmp, cc)) cc.SubtractBignum(tmp); break;
		case 5: cc.AddUInt64(r.next() >> r.below(60)); break;
		case 6: tmp.AssignUInt64(r.next() >> (8 + r.below(50))); if (Bignum::LessEqual(tmp, cc)) cc.SubtractBignum(tmp); break;
		case 7: set_operand(cc, rnd_hex(r, rnd_len(r, maxd)), sa); break;           // unrelated value
		case 8: set_operand(cc, rnd_hex(r, maxd + 1 > 700 ? 700 : maxd + 1), 0); break;
		case 9: cc.AssignBignum(c.a[k]); break;                // c == a
		case 10: cc.AssignBignum(c.b[k]); cc.AddBignum(c.b[k]); break;   // c == 2b (equals a+b only if a == b)
		default: cc.ShiftLeft(1); break;                       // c == 2(a+b)
		}
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
			c.n = 1;
			c.a = new Bignum[1]; c.b = new Bignum[1]; c.c = new Bignum[1];
			parse_operand(f[2], c.a[0]); parse_operand(f[3], c.b[0]); parse_operand(f[4], c.c[0]);
		}
		else build(c, strtoull(f[2].c_str(), 0, 10), atoi(f[3].c_str()), atoi(f[4].c_str()), atoi(f[5].c_str()));
		c.res.resize(c.n);
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
	for (size_t k = 0; k < c.n; ++k)
	{
		int v = Bignum::PlusCompare(c.a[k], c.b[k], c.c[k]);
		c.res[k] = v;
		s += static_cast<uint64_t>(v + 1);
	}
	return s;
}

static void digest(size_t i, tcb::Hash& h)
{
	for (size_t k = 0; k < g_cases[i].n; ++k) h.u64(static_cast<uint64_t>(g_cases[i].res[k] + 1));
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
