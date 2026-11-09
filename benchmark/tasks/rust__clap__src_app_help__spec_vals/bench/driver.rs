
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `Help::spec_vals`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use args::OptBuilder;
    use fmt::ColorWhen;
    use std::ffi::{OsStr, OsString};
    use std::time::Instant;

    const WORDS: [&str; 20] = ["fast", "slow", "vi", "emacs", "Nearest", "Linear", "Cubic", "Gaussian", "Lanczos3",
        "caf\u{e9}", "\u{6570}", "on", "off", "auto", "x", "always", "never", "\u{e4}-b", "json", "yaml"];

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

    fn opt(s: &'static str) -> Option<&'static str> { if s == "-" { None } else { Some(s) } }

    fn words(s: &'static str) -> Vec<&'static str> {
        if s.starts_with('#') {
            let mut it = s[1..].split(':');
            let count: usize = it.next().unwrap().parse().unwrap();
            let seed: usize = it.next().unwrap().parse().unwrap();
            (0..count).map(|i| &*Box::leak(format!("{}{}", WORDS[(seed + 7 * i) % WORDS.len()], i % 10).into_boxed_str())).collect()
        } else {
            s.split(' ').collect()
        }
    }

    struct Case { hide_pv: bool, o: OptBuilder<'static, 'static> }

    fn build(line: &'static str) -> Case {
        let f: Vec<&'static str> = line.split('\t').collect();
        let mut o = OptBuilder::new("arg");
        o.s.long = Some("arg");
        o.b.settings.set(ArgSettings::TakesValue);
        if f[0].contains('E') { o.b.settings.set(ArgSettings::HideEnvValues); }
        if f[0].contains('D') { o.b.settings.set(ArgSettings::HideDefaultValue); }
        if f[0].contains('P') { o.b.settings.set(ArgSettings::HidePossibleValues); }
        if let Some(e) = opt(f[2]) {
            let mut it = e.splitn(2, '=');
            let k: &'static str = it.next().unwrap();
            o.v.env = Some((OsStr::new(k), it.next().map(OsString::from)));
        }
        o.v.default_val = opt(f[3]).map(OsStr::new);
        if let Some(a) = opt(f[4]) {
            o.s.aliases = Some(words(a).into_iter().map(|w| if w.starts_with('!') { (&w[1..], false) } else { (w, true) }).collect());
        }
        o.v.possible_vals = opt(f[5]).map(words);
        Case { hide_pv: f[1] == "1", o: o }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let lines: &'static Vec<String> = Box::leak(Box::new(read_lines()));
        let cases: Vec<Case> = lines.iter().map(|l| build(l.as_str())).collect();
        let mut sink: Vec<u8> = Vec::new();
        let mut sink2: Vec<u8> = Vec::new();
        let cz = || Colorizer::new(ColorizerOption { use_stderr: false, when: ColorWhen::Never });
        let h0 = Help::new(&mut sink, false, false, false, cz(), Some(120), None, false);
        let h1 = Help::new(&mut sink2, false, true, false, cz(), Some(120), None, false);
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter() {
                let hp = if c.hide_pv { &h1 } else { &h0 };
                fnv(&mut h, &format!("{}\n", hp.spec_vals(&c.o)));
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter() {
                    let hp = if c.hide_pv { &h1 } else { &h0 };
                    acc = acc.wrapping_add(bb(hp).spec_vals(bb(&c.o)).len() as u64);
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
