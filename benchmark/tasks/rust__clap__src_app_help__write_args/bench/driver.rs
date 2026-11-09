
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Help::write_args`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::Arg;
    use fmt::ColorWhen;
    use std::cell::RefCell;
    use std::rc::Rc;
    use std::time::Instant;

    const WORDS: [&str; 20] = ["the", "input", "file", "to", "use", "sets", "a", "custom", "config", "level",
        "café", "\u{6570}\u{5b57}", "of", "verbosity", "and", "output", "directory", "print", "debug", "information"];

    fn read_lines() -> Vec<String> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| l.to_string()).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for b in s {
            *h ^= *b as u64;
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

    fn build(line: &str) -> (App<'static, 'static>, usize, u64) {
        let f: Vec<u64> = line.split('\t').map(|x| x.parse().unwrap()).collect();
        let mut r = R(f[6].wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1);
        let hid = f[5];
        let mut app = App::new("prog");
        for i in 0..f[2] {
            let name = leak(format!("flag{}{}", WORDS[r.below(5) as usize], i));
            let mut a = Arg::with_name(name).long(name).help(words(&mut r, 2, 8));
            if r.below(3) == 0 { a = a.short(leak(((b'a' + (i % 26) as u8) as char).to_string())); }
            if r.below(100) < hid { a = a.hidden(true); if r.below(3) == 0 { a = a.next_line_help(true); } }
            if r.below(10) == 0 { a = a.next_line_help(true); }
            if r.below(3) == 0 { a = a.display_order(r.below(5) as usize); }
            app = app.arg(a);
        }
        for i in 0..f[3] {
            let name = leak(format!("opt{}{}", WORDS[r.below(5) as usize], i));
            let mut a = Arg::with_name(name).long(name).takes_value(true).help(words(&mut r, 2, 8));
            if r.below(3) == 0 { a = a.short(leak(((b'A' + (i % 26) as u8) as char).to_string())); }
            if r.below(3) == 0 { a = a.value_name(WORDS[r.below(10) as usize]); }
            if r.below(4) == 0 { a = a.possible_values(&["fast", "slow", "auto"]); }
            if r.below(4) == 0 { a = a.default_value("dflt"); }
            if r.below(100) < hid { a = a.hidden(true); if r.below(3) == 0 { a = a.next_line_help(true); } }
            if r.below(3) == 0 { a = a.display_order(r.below(5) as usize); }
            app = app.arg(a);
        }
        for i in 0..f[4] {
            let name = leak(format!("pos{}{}", WORDS[r.below(5) as usize], i));
            let mut a = Arg::with_name(name).index(i + 1).help(words(&mut r, 1, 6));
            if r.below(5) == 0 { a = a.multiple(true); }
            if r.below(100) < hid { a = a.hidden(true); }
            app = app.arg(a);
        }
        (app, if f[1] == 0 { usize::MAX } else { f[1] as usize }, f[0])
    }

    #[derive(Clone)]
    struct Sink(Rc<RefCell<Vec<u8>>>);
    impl Write for Sink {
        fn write(&mut self, b: &[u8]) -> io::Result<usize> { self.0.borrow_mut().extend_from_slice(b); Ok(b.len()) }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    fn call(h: &mut Help, c: &(App<'static, 'static>, usize, u64)) {
        h.term_w = c.1;
        h.longest = 0;
        h.force_next_line = false;
        let p = &c.0.p;
        let res = match c.2 {
            0 => h.write_args(p.flags().map(as_arg_trait).chain(p.opts().map(as_arg_trait))),
            1 => h.write_args(p.flags().map(as_arg_trait)),
            2 => h.write_args(p.opts().map(as_arg_trait)),
            _ => h.write_args(p.positionals().map(as_arg_trait)),
        };
        res.expect("write_args");
        let l = h.longest;
        h.writer.write_all(format!("\x00{}", l).as_bytes()).expect("io");
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let cases: Vec<(App<'static, 'static>, usize, u64)> = read_lines().iter().map(|l| build(l)).collect();
        let buf = Rc::new(RefCell::new(Vec::new()));
        let mut sink = Sink(buf.clone());
        let cz = Colorizer::new(ColorizerOption { use_stderr: false, when: ColorWhen::Never });
        let mut h = Help::new(&mut sink, false, false, false, cz, Some(120), None, false);
        if mode == "check" {
            let mut d: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                call(&mut h, c);
                let out = buf.borrow().clone();
                buf.borrow_mut().clear();
                fnv(&mut d, &out);
                fnv(&mut d, b"\x00|\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), d);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    call(bb(&mut h), bb(c));
                    acc = acc.wrapping_add(buf.borrow().len() as u64);
                    buf.borrow_mut().clear();
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
