
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `gen_fish_inner`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use app::App;
    use args::{Arg, SubCommand};
    use std::time::Instant;

    const WORDS: [&str; 16] = ["sets", "the", "config", "file", "it's", "a", "\"quoted\"", "back\\slash", "value",
        "caf\u{e9}", "\u{6570}\u{5b57}", "don't", "path\\to\\it", "of", "output", "level"];

    fn read_lines() -> Vec<String> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| l.to_string()).collect()
    }

    fn fnv(h: &mut u64, s: &str) {
        for b in s.bytes() {
            *h ^= b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    fn bb<T>(x: T) -> T { let y = unsafe { std::ptr::read_volatile(&x) }; std::mem::forget(x); y }
    fn leak(s: String) -> &'static str { Box::leak(s.into_boxed_str()) }

    struct R(u64);
    impl R {
        fn next(&mut self) -> u64 { self.0 ^= self.0 << 13; self.0 ^= self.0 >> 7; self.0 ^= self.0 << 17; self.0 }
        fn below(&mut self, n: u64) -> u64 { self.next() % n }
    }

    fn words(r: &mut R, lo: u64, span: u64) -> &'static str {
        let n = (lo + r.below(span)) as usize;
        leak((0..n).map(|_| WORDS[r.below(WORDS.len() as u64) as usize]).collect::<Vec<_>>().join(" "))
    }

    fn tree(r: &mut R, name: &str, n_opts: u64, n_flags: u64, n_sub: u64, depth: u64) -> App<'static, 'static> {
        let mut app = App::new(name.to_string());
        if r.below(4) != 0 { app = app.about(words(r, 1, 6)); }
        for i in 0..(n_opts / 2 + r.below(n_opts + 1)) {
            let nm = leak(format!("opt{}", i));
            let mut a = Arg::with_name(nm).takes_value(true);
            let k = r.below(3);
            if k != 1 { a = a.long(nm); }
            if k != 0 { a = a.short(leak(((b'a' + (i % 26) as u8) as char).to_string())); }
            if r.below(5) != 0 { a = a.help(words(r, 1, 8)); }
            if r.below(3) == 0 { a = a.possible_values(&["fast", "slow", "auto-detect"]); }
            app = app.arg(a);
        }
        for i in 0..(n_flags / 2 + r.below(n_flags + 1)) {
            let nm = leak(format!("flag{}", i));
            let mut a = Arg::with_name(nm);
            let k = r.below(3);
            if k != 1 { a = a.long(nm); }
            if k != 0 { a = a.short(leak(((b'A' + (i % 26) as u8) as char).to_string())); }
            if r.below(5) != 0 { a = a.help(words(r, 1, 8)); }
            app = app.arg(a);
        }
        if depth > 0 {
            for i in 0..n_sub {
                let sub = tree(r, &format!("sub{}-{}", depth, i), n_opts, n_flags, n_sub, depth - 1);
                app = app.subcommand(sub);
            }
        }
        app
    }

    struct Case { root: String, parent: String, app: App<'static, 'static> }

    fn build(line: &str) -> Case {
        let f: Vec<&str> = line.split('\t').collect();
        let n: Vec<u64> = f[2..].iter().map(|x| x.parse().unwrap()).collect();
        let mut r = R(n[4].wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1);
        let app = tree(&mut r, f[0], n[0], n[1], n[2], n[3]);
        let _ = SubCommand::with_name("unused");
        Case { root: f[0].to_string(), parent: if f[1] == "-" { String::new() } else { f[1].to_string() }, app: app }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases: Vec<Case> = read_lines().iter().map(|l| build(l)).collect();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let mut buf = String::new();
                gen_fish_inner(&c.root, &FishGen::new(&c.app.p), &c.parent, &mut buf);
                fnv(&mut h, &buf);
                fnv(&mut h, "\x00\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let mut buf = String::new();
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    buf.clear();
                    gen_fish_inner(bb(&c.root), &FishGen::new(&bb(c).app.p), &c.parent, &mut buf);
                    acc = acc.wrapping_add(buf.len() as u64);
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
