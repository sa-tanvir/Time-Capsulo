// Time Capsulo bench driver for `convert_number_to_string`. argv: <size> <repeat> <mode>   (mode = check | time)
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

struct Case { bool oom; std::vector<double> v; int reps; };
static std::vector<Case> g_cases;
static tcb::Hash g_hash;

static void* failing_allocate(size_t) { return 0; }
static void plain_deallocate(void* p) { free(p); }
static void* plain_allocate(size_t n) { return malloc(n); }

static double from_bits(uint64_t b) { double d; memcpy(&d, &b, sizeof d); return d; }

static std::vector<double> expand(uint64_t seed, size_t n, int kind)
{
	tcb::Rng r(seed);
	std::vector<double> v;
	v.reserve(n);
	for (size_t i = 0; i < n; ++i)
	{
		double d = 0;
		int k = kind == 4 ? static_cast<int>(r.below(4)) : kind;
		switch (k)
		{
		case 0: // random mantissa, exponent over the whole double range
		{
			uint64_t bits = (r.next() & 0x800FFFFFFFFFFFFFULL) | (static_cast<uint64_t>(r.below(2046) + 1) << 52);
			d = from_bits(bits);
			break;
		}
		case 1: // integers up to 2^60
			d = static_cast<double>(r.next() >> (4 + r.below(60)));
			if (r.below(2)) d = -d;
			break;
		case 2: // decimals with few fractional digits
		{
			double scale = 1;
			for (uint64_t j = r.below(12); j > 0; --j) scale *= 10;
			d = static_cast<double>(static_cast<int64_t>(r.next() >> 24) - (1LL << 39)) / scale;
			break;
		}
		default: // specials and neighbours of powers of ten
		{
			uint64_t s = r.below(10);
			if (s == 0) d = from_bits(0x7FF8000000000000ULL);
			else if (s == 1) d = from_bits(0x7FF0000000000000ULL);
			else if (s == 2) d = from_bits(0xFFF0000000000000ULL);
			else if (s == 3) d = 0.0;
			else if (s == 4) d = from_bits(0x8000000000000000ULL);
			else if (s == 5) d = from_bits(1 + r.below(1ULL << 52));            // denormal
			else
			{
				d = 1;
				int e = static_cast<int>(r.below(600)) - 300;
				for (int j = 0; j < (e < 0 ? -e : e); ++j) d = e < 0 ? d / 10 : d * 10;
				d *= (1 + static_cast<double>(r.below(3)) * 0.5);
			}
			break;
		}
		}
		v.push_back(d);
	}
	return v;
}

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[1].c_str());
		c.oom = (f[0] == "O");
		if (f[0] == "L" || f[0] == "O")   // L|O reps hexbits,hexbits,...   (O: the allocator cannot provide memory)
		{
			const std::string& l = f.size() > 2 ? f[2] : std::string();
			size_t pos = 0;
			while (pos < l.size())
			{
				size_t comma = l.find(',', pos);
				if (comma == std::string::npos) comma = l.size();
				c.v.push_back(from_bits(strtoull(l.substr(pos, comma - pos).c_str(), 0, 16)));
				pos = comma + 1;
			}
		}
		else c.v = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[3].c_str())), atoi(f[4].c_str()));   // G reps seed n kind
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }
static void reset(size_t) { g_hash = tcb::Hash(); }

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	xpath_memory_block block;
	block.next = 0;
	block.capacity = c.oom ? 0 : sizeof(block.data);
	xpath_allocator alloc(&block);
	if (c.oom) set_memory_management_functions(failing_allocate, plain_deallocate);
	uint64_t sum = 0;
	for (size_t k = 0; k < c.v.size(); ++k)
	{
		alloc._root_size = 0;   // every conversion starts with an empty page, the previous result is already consumed
		xpath_string s = convert_number_to_string(c.v[k], &alloc);
		const char_t* p = s.c_str();
		size_t len = strlen(p);
		g_hash.u64(len);
		g_hash.add(p, len);
		sum += len + static_cast<unsigned char>(len ? p[len - 1] : 0);
	}
	if (c.oom) set_memory_management_functions(plain_allocate, plain_deallocate);
	return sum;
}

static void digest(size_t, tcb::Hash& h) { h.u64(g_hash.h); }

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
