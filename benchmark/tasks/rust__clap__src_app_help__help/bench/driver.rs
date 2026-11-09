
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Help::help`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::{Base, FlagBuilder, OptBuilder, PosBuilder, Switched, Valued};
    use fmt::ColorWhen;
    use std::cell::RefCell;
    use std::rc::Rc;
    use std::time::Instant;

    const WORDS: [&str; 24] = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "configuration",
        "file", "to", "use", "when", "a", "value", "café", "\u{6570}\u{5b57}", "of", "and", "argument",
        "incomprehensibilities", "x", "program", "sets"];

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

    fn text(s: &str) -> Option<&'static str> {
        if s == "-" { return None; }
        if s.starts_with('=') { return Some(leak(s[1..].replace("\\n", "\n"))); }
        let p: Vec<i64> = s[1..].split(':').map(|x| x.parse().unwrap()).collect();
        let (n, seed, nl) = (p[0] as usize, p[1] as usize, p[2]);
        let mut out = String::new();
        for i in 0..n {
            if i > 0 {
                if nl > 0 && i % (nl as usize) == 0 { out.push_str("{n}"); }
                else if nl < 0 && i % ((-nl) as usize) == 0 { out.push('\n'); }
                else { out.push(' '); }
            }
            out.push_str(WORDS[(seed + 5 * i) % WORDS.len()]);
        }
        Some(leak(out))
    }

    #[derive(Clone)]
    struct Sink(Rc<RefCell<Vec<u8>>>);
    impl Write for Sink {
        fn write(&mut self, b: &[u8]) -> io::Result<usize> { self.0.borrow_mut().extend_from_slice(b); Ok(b.len()) }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    enum A { O(OptBuilder<'static, 'static>), F(FlagBuilder<'static, 'static>), P(PosBuilder<'static, 'static>) }
    struct Case { a: A, spec: &'static str, nlh: bool, use_long: bool, force: bool, term_w: usize, longest: usize }

    fn build(line: &'static str) -> Case {
        let f: Vec<&'static str> = line.split('\t').collect();
        let mut b = Base::new("arg");
        if f[1].contains('N') { b.settings.set(ArgSettings::NextLineHelp); }
        b.help = text(f[2]);
        b.long_help = text(f[3]);
        let mut s = Switched::default();
        let a = match f[0] {
            "O" => { s.long = Some("opt"); b.settings.set(ArgSettings::TakesValue);
                     A::O(OptBuilder { b: b, s: s, v: Valued::default() }) }
            "F" => { s.short = Some('f'); A::F(FlagBuilder { b: b, s: s }) }
            _ => { b.settings.set(ArgSettings::TakesValue); A::P(PosBuilder { b: b, v: Valued::default(), index: 1 }) }
        };
        let tw: usize = f[8].parse().unwrap();
        Case { a: a, spec: text(f[4]).unwrap_or(""), nlh: f[5] == "1", use_long: f[6] == "1", force: f[7] == "1",
               term_w: if tw == 0 { usize::MAX } else { tw }, longest: f[9].parse().unwrap() }
    }

    fn call(h: &mut Help, c: &Case) {
        h.next_line_help = c.nlh;
        h.use_long = c.use_long;
        h.force_next_line = c.force;
        h.term_w = c.term_w;
        h.longest = c.longest;
        let r = match c.a { A::O(ref x) => h.help(x, c.spec), A::F(ref x) => h.help(x, c.spec), A::P(ref x) => h.help(x, c.spec) };
        r.expect("io");
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let lines: &'static Vec<String> = Box::leak(Box::new(read_lines()));
        let cases: Vec<Case> = lines.iter().map(|l| build(l.as_str())).collect();
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
