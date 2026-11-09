// Time Capsulo bench driver for `string_value`. argv: <size> <repeat> <mode>   (mode = check | time)
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

#include <unordered_map>

using namespace pugi;
using namespace pugi::impl;

struct Case
{
	xml_document* doc;
	std::vector<xpath_node> sel;   // nodes (and attributes) whose string value is requested
	int reps;
};
static std::vector<Case> g_cases;
static xpath_memory_block g_block;
static xpath_allocator* g_alloc = 0;
static std::vector<xpath_string> g_results;

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

static std::string expand(uint64_t seed, size_t nitems, unsigned maxdepth)
{
	tcb::Rng r(seed);
	std::string s = "<root>";
	std::vector<std::string> open;
	open.push_back("root");
	size_t count = 0, tag = 0;
	char buf[64];
	while (count < nitems)
	{
		uint64_t k = r.below(100);
		if (k < 30 && open.size() < maxdepth)
		{
			snprintf(buf, sizeof buf, "e%u", static_cast<unsigned>(tag++ % 7));
			s += "<"; s += buf;
			for (uint64_t a = r.below(3); a > 0; --a) { snprintf(buf + 8, 40, " a%u='v%u&amp;%u'", static_cast<unsigned>(r.below(5)), static_cast<unsigned>(r.below(100)), static_cast<unsigned>(a)); s += buf + 8; }
			s += ">";
			snprintf(buf, sizeof buf, "e%u", static_cast<unsigned>((tag - 1) % 7));
			open.push_back(buf);
			++count;
		}
		else if (k < 52 && open.size() > 1) { s += "</" + open.back() + ">"; open.pop_back(); ++count; }
		else if (k < 80)
		{
			size_t len = 1 + r.below(12);
			for (size_t i = 0; i < len; ++i) s.push_back("abcdefghij klmnopqrstuvwxyz0123456789"[r.below(37)]);
			if (r.below(8) == 0) s += "&lt;&#65;";
			++count;
		}
		else if (k < 87) { s += "<![CDATA[cd"; for (uint64_t i = r.below(6); i > 0; --i) s.push_back("xyz<>&"[r.below(6)]); s += "]]>"; ++count; }
		else if (k < 93) { s += "<!--c" + std::string(1, "abc"[r.below(3)]) + "-->"; ++count; }
		else if (k < 97) { s += "<?pi d" + std::string(1, "123"[r.below(3)]) + "?>"; ++count; }
		else { snprintf(buf, sizeof buf, "<leaf%u/>", static_cast<unsigned>(r.below(10))); s += buf; ++count; }
	}
	while (!open.empty()) { s += "</" + open.back() + ">"; open.pop_back(); }
	return s;
}

static void collect(Case& c)
{
	std::vector<xml_node> pre;
	std::vector<size_t> parent_idx;
	// iterative preorder walk of the document
	pre.push_back(*c.doc); parent_idx.push_back(0);
	{
		std::vector<std::pair<xml_node, size_t> > st;
		for (xml_node ch = c.doc->last_child(); ch; ch = ch.previous_sibling()) st.push_back(std::make_pair(ch, size_t(0)));
		while (!st.empty())
		{
			std::pair<xml_node, size_t> top = st.back(); st.pop_back();
			size_t idx = pre.size();
			pre.push_back(top.first); parent_idx.push_back(top.second);
			for (xml_node ch = top.first.last_child(); ch; ch = ch.previous_sibling()) st.push_back(std::make_pair(ch, idx));
		}
	}
	std::vector<size_t> sz(pre.size(), 1);
	for (size_t i = pre.size(); i-- > 1;) sz[parent_idx[i]] += sz[i];
	size_t total = pre.size();
	size_t budget = 30 * total + 100;
	size_t used = 0;
	size_t stride = total / 150 + 1;
	c.sel.push_back(xpath_node(*c.doc));
	used += total;
	for (size_t i = 1; i < pre.size(); ++i)
	{
		bool pick = (i % stride == 0) || i < 12;
		if (!pick || used + sz[i] > budget) continue;
		used += sz[i];
		c.sel.push_back(xpath_node(pre[i]));
		int na = 0;
		for (xml_attribute a = pre[i].first_attribute(); a && na < 3; a = a.next_attribute(), ++na) c.sel.push_back(xpath_node(a, pre[i]));
	}
}

static void prepare(const std::vector<std::string>& lines)
{
	for (size_t i = 0; i < lines.size(); ++i)
	{
		std::vector<std::string> f = tcb::split_tabs(lines[i]);
		Case c;
		c.reps = atoi(f[1].c_str());
		unsigned flags = parse_default | parse_comments | parse_pi | parse_declaration | parse_doctype;
		std::string text;
		if (f[0] == "L")   // L reps embed text
		{
			if (atoi(f[2].c_str())) flags |= parse_embed_pcdata;
			text = f.size() > 3 ? unescape(f[3]) : std::string();
		}
		else               // G reps seed items maxdepth embed
		{
			if (atoi(f[5].c_str())) flags |= parse_embed_pcdata;
			text = expand(strtoull(f[2].c_str(), 0, 10), static_cast<size_t>(atol(f[3].c_str())), static_cast<unsigned>(atoi(f[4].c_str())));
		}
		c.doc = new xml_document();
		if (!c.doc->load_buffer(text.data(), text.size(), flags)) { fprintf(stderr, "workload document %zu does not parse\n", i); exit(3); }
		collect(c);
		g_cases.push_back(c);
	}
}

static size_t ncases() { return g_cases.size(); }
static int reps(size_t i) { return g_cases[i].reps; }

static void reset(size_t)
{
	if (g_alloc) { g_alloc->release(); delete g_alloc; g_alloc = 0; }
	g_results.clear();
	g_block.next = 0;
	g_block.capacity = sizeof(g_block.data);
	g_alloc = new xpath_allocator(&g_block);
}

static uint64_t exec(size_t i)
{
	const Case& c = g_cases[i];
	g_results.reserve(c.sel.size());
	uint64_t sum = 0;
	for (size_t k = 0; k < c.sel.size(); ++k)
	{
		g_results.push_back(string_value(c.sel[k], g_alloc));
		sum += g_results.back().length();
	}
	return sum;
}

static void digest(size_t i, tcb::Hash& h)
{
	h.u64(g_results.size());
	for (size_t k = 0; k < g_results.size(); ++k)
	{
		h.u64(g_results[k].length());
		h.add(g_results[k].c_str(), g_results[k].length());
	}
	(void)i;
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
