
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Help::write_templated_help`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::{Arg, SubCommand};
    use fmt::ColorWhen;
    use std::cell::RefCell;
    use std::rc::Rc;
    use std::time::Instant;

    // tags are weighted: cheap tags and plain text dominate, expensive section tags are rare
    const PIECES: [&str; 40] = ["{bin}", "{version}", "{author}", "{about}", "{long-about}", "{after-help}",
        "{before-help}", "{?}", "{unknown}", "{BIN}", "{}", "{ bin }", "{a-much-too-long-tag-name}", "{{bin}",
        "}", "{exactly14chars}", "{bin}", "{version}", "{author}", "{about}", "{bin}", "{nope", "\n", "\n\n",
        " ", "    ", "USAGE:", "text ", "caf\u{e9} ", "\u{6570}\u{5b57} ", "lorem ipsum dolor ", "--flag ",
        "<FILE> ", "[OPTIONS] ", "sit amet, ", "e", "{flags}", "{usage}", "{subcommands}", "{positionals}"];

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

    struct R(u64);
    impl R {
        fn next(&mut self) -> u64 { self.0 ^= self.0 << 13; self.0 ^= self.0 >> 7; self.0 ^= self.0 << 17; self.0 }
    }

    fn unesc(s: &str) -> String {
        let mut out = String::new();
        let mut it = s.chars();
        while let Some(c) = it.next() {
            if c == '\\' {
                match it.next() { Some('n') => out.push('\n'), Some('t') => out.push('\t'), Some(x) => out.push(x), None => {} }
            } else { out.push(c); }
        }
        out
    }

    fn gen(n: usize, seed: u64) -> String {
        let mut r = R(seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1);
        let mut out = String::new();
        for _ in 0..n {
            let mut k = (r.next() % PIECES.len() as u64) as usize;
            // section tags (last 4) are 10x rarer
            if k >= PIECES.len() - 4 && r.next() % 10 != 0 { k = (r.next() % 26) as usize; }
            out.push_str(PIECES[k]);
        }
        out
    }

    fn apps() -> Vec<App<'static, 'static>> {
        let full = App::new("MyApp").version("1.0").author("Kevin K. <kbknapp@gmail.com>")
            .about("Does awesome things").long_about("Does awesome things, at length")
            .before_help("Before the help").after_help("After the help")
            .arg(Arg::with_name("debug").short("d").help("Turn debugging information on"))
            .arg(Arg::with_name("config").short("c").long("config").value_name("FILE").help("Sets a custom config file"))
            .arg(Arg::with_name("output").help("Sets an optional output file"))
            .subcommand(SubCommand::with_name("test").about("does testing things"));
        let bare = App::new("bare");
        let mut sub = App::new("mv").arg(Arg::with_name("src").required(true).help("source"));
        sub.p.meta.bin_name = Some("git mv".to_string());
        vec![full, bare, sub]
    }

    #[derive(Clone)]
    struct Sink(Rc<RefCell<Vec<u8>>>);
    impl Write for Sink {
        fn write(&mut self, b: &[u8]) -> io::Result<usize> { self.0.borrow_mut().extend_from_slice(b); Ok(b.len()) }
        fn flush(&mut self) -> io::Result<()> { Ok(()) }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let apps = apps();
        let cases: Vec<(usize, String)> = read_lines().iter().map(|l| {
            let f: Vec<&str> = l.splitn(3, '\t').collect();
            let app: usize = f[1].parse().unwrap();
            if f[0] == "L" { (app, unesc(f.get(2).cloned().unwrap_or(""))) } else {
                let g: Vec<u64> = f[2].split('\t').map(|x| x.parse().unwrap()).collect();
                (app, gen(g[0] as usize, g[1]))
            }
        }).collect();
        let buf = Rc::new(RefCell::new(Vec::new()));
        let mut sink = Sink(buf.clone());
        let cz = Colorizer::new(ColorizerOption { use_stderr: false, when: ColorWhen::Never });
        let mut h = Help::new(&mut sink, false, false, false, cz, Some(120), None, false);
        if mode == "check" {
            let mut d: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let r = h.write_templated_help(&apps[c.0].p, &c.1);
                let out = buf.borrow().clone();
                buf.borrow_mut().clear();
                fnv(&mut d, &out);
                fnv(&mut d, format!("\x00|{}\n", r.is_ok()).as_bytes());
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), d);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    let r = bb(&mut h).write_templated_help(&apps[c.0].p, bb(&c.1));
                    acc = acc.wrapping_add(buf.borrow().len() as u64 + r.is_ok() as u64);
                    buf.borrow_mut().clear();
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
