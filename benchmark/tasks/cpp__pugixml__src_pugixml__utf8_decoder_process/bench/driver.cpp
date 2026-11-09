// Time Capsulo bench driver for `utf8_decoder::process`. argv: <size> <repeat> <mode>   (mode = check | time)
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

// trait ids: 0 utf16_writer, 1 utf32_writer, 2 latin1_writer, 3 utf8_writer, 4 utf16_counter, 5 utf32_counter, 6 utf8_counter
struct Case { int trait; unsigned off; std::vector<uint8_t> bytes; int reps; };
static std::vector<Case> g_cases;
static std::vector<uint8_t> g_in;      // input copy with `off` leading padding bytes (alignment varies per case)
static std::vector<uint64_t> g_out;    // output area (8 bytes per input byte is more than enough)
static size_t g_count;                 // number of output units / bytes / counter value
static uint64_t g_units_bytes;

static void put_utf8(std::vector<uint8_t>& v, uint32_t cp)
{
	if (cp < 0x80) v.push_back(static_cast<uint8_t>(cp));
	else if (cp < 0x800) { v.push_back(0xC0 | (cp >> 6)); v.push_back(0x80 | (cp & 63)); }
	else if (cp < 0x10000) { v.push_back(0xE0 | (cp >> 12)); v.push_back(0x80 | ((cp >> 6) & 63)); v.push_back(0x80 | (cp & 63)); }
	else { v.push_back(0xF0 | (cp >> 18)); v.push_back(0x80 | ((cp >> 12) & 63)); v.push_back(0x80 | ((cp >> 6) & 63)); v.push_back(0x80 | (cp & 63)); }
}

// mix: percentage of "damaged" items (stray continuation bytes, truncated sequences, 0xF8+ bytes, overlong leads)
static std::vector<uint8_t> expand(uint64_t seed, size_t len, unsigned ascii_pct, unsigned mix)
{
	tcb::Rng r(seed);
	std::vector<uint8_t> v;
	while (v.size() < len)
	{
		if (r.below(100) < mix)
		{
			switch (r.below(6))
			{
			case 0: v.push_back(0x80 + r.below(64)); break;                      // stray continuation byte
			case 1: v.push_back(0xC2 + r.below(30)); break;                      // lead byte without continuation
			case 2: v.push_back(0xE0 + r.below(16)); v.push_back(0x80 + r.below(64)); break;   // truncated 3-byte
			case 3: v.push_back(0xF0 + r.below(8)); v.push_back(0x80 + r.below(64)); v.push_back(0x80 + r.below(64)); break; // truncated 4-byte
			case 4: v.push_back(0xF8 + r.below(8)); break;                       // invalid lead
			default: v.push_back(0xC0 + r.below(2)); v.push_back(0x80 + r.below(64)); break;   // overlong 2-byte lead
			}
			continue;
		}
		if (r.below(100) < ascii_pct)
		{
			size_t run = 1 + r.below(24);
			for (size_t i = 0; i < run; ++i) v.push_back(static_cast<uint8_t>(1 + r.below(127)));
			continue;
		}
		uint64_t cls = r.below(10);
		uint32_t cp;
		if (cls < 4) cp = 0x80 + static_cast<uint32_t>(r.below(0x800 - 0x80));
		else if (cls < 8) cp = 0x800 + static_cast<uint32_t>(r.below(0x10000 - 0x800));   // includes surrogate code points (not validated)
		else cp = 0x10000 + static_cast<uint32_t>(r.below(0x110000 - 0x10000));
		put_utf8(v, cp);
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
		if (f[0] == "L")   // L reps trait off hexbytes
		{
			c.trait = atoi(f[2].c_str());
			c.off = static_cast<unsigned>(atoi(f[3].c_str()));
			const std::string& h = f.size() > 4 ? f[4] : std::string();
			for (size_t k = 0; k + 1 < h.size(); k += 2) c.bytes.push_back(static_cast<uint8_t>(strtoul(h.substr(k, 2).c_str(), 0, 16)));
		}
		else               // G reps seed trait off len ascii_pct mix
		{
			c.trait = atoi(f[3].c_str());
			c.off = static_cast<unsigned>(atoi(f[4].c_str()));
			c.bytes = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[5].c_str())), static_cast<unsigned>(atoi(f[6].c_str())), static_cast<unsigned>(atoi(f[7].c_str())));
		}
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t i)
{
	const Case& c = g_cases[i];
	g_in.assign(c.off, 0);
	g_in.insert(g_in.end(), c.bytes.begin(), c.bytes.end());
	g_in.push_back(0);
	g_out.assign(c.bytes.size() + 4, 0);
}

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	const uint8_t* data = &g_in[0] + c.off;
	size_t n = c.bytes.size();
	switch (c.trait)
	{
	case 0: { uint16_t* b = reinterpret_cast<uint16_t*>(&g_out[0]); g_count = utf8_decoder::process(data, n, b, utf16_writer()) - b; g_units_bytes = 2; break; }
	case 1: { uint32_t* b = reinterpret_cast<uint32_t*>(&g_out[0]); g_count = utf8_decoder::process(data, n, b, utf32_writer()) - b; g_units_bytes = 4; break; }
	case 2: { uint8_t* b = reinterpret_cast<uint8_t*>(&g_out[0]); g_count = utf8_decoder::process(data, n, b, latin1_writer()) - b; g_units_bytes = 1; break; }
	case 3: { uint8_t* b = reinterpret_cast<uint8_t*>(&g_out[0]); g_count = utf8_decoder::process(data, n, b, utf8_writer()) - b; g_units_bytes = 1; break; }
	case 4: g_count = utf8_decoder::process(data, n, size_t(0), utf16_counter()); g_units_bytes = 0; break;
	case 5: g_count = utf8_decoder::process(data, n, size_t(0), utf32_counter()); g_units_bytes = 0; break;
	default: g_count = utf8_decoder::process(data, n, size_t(0), utf8_counter()); g_units_bytes = 0; break;
	}
	return g_count;
}

static void digest(size_t, tcb::Hash& h)
{
	h.u64(g_count);
	h.add(&g_out[0], g_count * g_units_bytes);
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
