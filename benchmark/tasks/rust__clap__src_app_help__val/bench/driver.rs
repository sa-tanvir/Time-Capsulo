
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Help::val`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::{Base, FlagBuilder, OptBuilder, PosBuilder, Switched, Valued};
    use fmt::ColorWhen;
    use std::cell::RefCell;
    use std::rc::Rc;
    use std::time::Instant;

    const WORDS: [&str; 20] = ["file", "name", "val", "path", "out", "in", "x", "level", "mode", "the", "café",
        "\u{6570}\u{5b57}", "of", "and", "argument", "value", "to", "program", "some", "configuration"];

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

    fn opt(s: &'static str) -> Option<&'static str> { if s == "-" { None } else { Some(s) } }
    fn leak(s: String) -> &'static str { Box::leak(s.into_boxed_str()) }

    #[derive(Clone)]
    struct Sink(Rc<RefCell<Vec<u8>>>);
    impl Write for Sink {
        fn write(&mut self, b: &[u8]) -> io::Result<usize> { self.0.borrow_mut().extend_from_slice(b); Ok(b.len()) }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    enum A { O(OptBuilder<'static, 'static>), F(FlagBuilder<'static, 'static>), P(PosBuilder<'static, 'static>) }
    struct Case { a: A, nlh: bool, term_w: usize, longest: usize }

    fn build(line: &'static str) -> Case {
        let f: Vec<&'static str> = line.split('\t').collect();
        let mut b = Base::new("arg");
        for (c, s) in [('M', ArgSettings::Multiple), ('D', ArgSettings::RequireDelimiter),
                       ('E', ArgSettings::RequireEquals), ('N', ArgSettings::NextLineHelp)].iter() {
            if f[3].contains(*c) { b.settings.set(*s); }
        }
        if let Some(n) = opt(f[7]) {
            let n: usize = n.parse().unwrap();
            b.help = Some(leak((0..n).map(|i| WORDS[(i * 3) % WORDS.len()]).collect::<Vec<_>>().join(" ")));
        }
        let mut v = Valued::default();
        v.val_delim = opt(f[4]).map(|s| s.chars().next().unwrap());
        v.num_vals = opt(f[5]).map(|s| s.parse().unwrap());
        if let Some(names) = opt(f[6]) {
            let mut vm = VecMap::new();
            if names.starts_with('#') {
                let mut it = names[1..].split(':');
                let count: usize = it.next().unwrap().parse().unwrap();
                let seed: usize = it.next().unwrap().parse().unwrap();
                for i in 0..count { vm.insert(i, WORDS[(seed + 7 * i) % WORDS.len()]); }
            } else {
                for (i, n) in names.split(' ').enumerate() { vm.insert(i, n); }
            }
            v.val_names = Some(vm);
        }
        let npv: usize = f[8].parse().unwrap();
        if npv > 0 { v.possible_vals = Some((0..npv).map(|i| WORDS[i % WORDS.len()]).collect()); }
        let mut s = Switched::default();
        s.long = opt(f[1]);
        s.short = opt(f[2]).map(|x| x.chars().next().unwrap());
        let a = match f[0] {
            "O" => { b.settings.set(ArgSettings::TakesValue); A::O(OptBuilder { b: b, s: s, v: v }) }
            "F" => A::F(FlagBuilder { b: b, s: s }),
            _ => { b.settings.set(ArgSettings::TakesValue); A::P(PosBuilder { b: b, v: v, index: 1 }) }
        };
        let sig = match a { A::O(ref x) => x.to_string(), A::F(ref x) => x.to_string(), A::P(ref x) => x.to_string() };
        let tw: usize = f[10].parse().unwrap();
        Case { a: a, nlh: f[9] == "1", term_w: if tw == 0 { usize::MAX } else { tw },
               longest: str_width(&sig) + f[11].parse::<usize>().unwrap() }
    }

    fn call(h: &mut Help, c: &Case) -> (String, bool) {
        h.next_line_help = c.nlh;
        h.term_w = c.term_w;
        h.longest = c.longest;
        h.force_next_line = false;
        let r = match c.a { A::O(ref x) => h.val(x), A::F(ref x) => h.val(x), A::P(ref x) => h.val(x) };
        (r.expect("io"), h.force_next_line)
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
                let (sv, fnl) = call(&mut h, c);
                let out = buf.borrow().clone();
                buf.borrow_mut().clear();
                fnv(&mut d, &out);
                fnv(&mut d, format!("|{}|{}\n", sv, fnl).as_bytes());
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), d);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    let (sv, fnl) = call(bb(&mut h), bb(c));
                    acc = acc.wrapping_add(sv.len() as u64 + fnl as u64 + buf.borrow().len() as u64);
                    buf.borrow_mut().clear();
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
