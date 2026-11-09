
#[cfg(test)]
mod tc_bench {
    // Time Capsulo bench driver for `decode_helper`. Env: TC_SIZE, TC_REPEAT, TC_MODE (check|time), TC_TASK.
    use super::*;
    use crate::{encode_config, CharacterSet};
    use std::time::Instant;

    fn rand_bytes(n: usize, seed: u64) -> Vec<u8> {
        let mut x = seed | 1;
        (0..n).map(|_| {
            x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
            (x.wrapping_mul(0x2545_F491_4F6C_DD1D) >> 56) as u8
        }).collect()
    }

    fn charset(s: &str) -> CharacterSet {
        match s { "S" => CharacterSet::Standard, "U" => CharacterSet::UrlSafe, _ => CharacterSet::Crypt }
    }

    fn unhex(s: &str) -> Vec<u8> {
        (0..s.len() / 2).map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).unwrap()).collect()
    }

    struct Case { input: Vec<u8>, config: Config, out: Vec<u8> }

    fn load() -> Vec<Case> {
        let task = std::env::var("TC_TASK").unwrap_or_else(|_| "/task".to_string());
        let size = std::env::var("TC_SIZE").expect("TC_SIZE");
        let text = std::fs::read_to_string(format!("{}/bench/workload_{}.txt", task, size)).expect("workload");
        text.lines().filter(|l| !l.is_empty()).map(|l| {
            let f: Vec<&str> = l.split('\t').collect();
            let cs = charset(f[1]);
            let allow = f[2] == "1";
            let input = if f[0] == "lit" {
                unhex(f.get(3).cloned().unwrap_or(""))
            } else {
                let pad = f[3] == "1";
                let raw = rand_bytes(f[4].parse().unwrap(), f[5].parse().unwrap());
                let mut e = encode_config(&raw, Config::new(cs, pad)).into_bytes();
                let m: Vec<&str> = f[6].split(':').collect();
                match m[0] {
                    "set" => { let p: usize = m[1].parse().unwrap(); e[p] = m[2].parse().unwrap(); }
                    "cut" => { let k: usize = m[1].parse().unwrap(); let n = e.len() - k; e.truncate(n); }
                    _ => {}
                }
                e
            };
            let config = Config::new(cs, true).decode_allow_trailing_bits(allow);
            let out = vec![0u8; num_chunks(&input) * 6];
            Case { input, config, out }
        }).collect()
    }

    fn fnv(h: &mut u64, s: &[u8]) {
        for b in s {
            *h ^= *b as u64;
            *h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }

    #[test]
    fn tc_bench() {
        let mode = match std::env::var("TC_MODE") { Ok(m) => m, Err(_) => return };
        let repeat: usize = std::env::var("TC_REPEAT").ok().and_then(|r| r.parse().ok()).unwrap_or(1);
        let mut cases = load();
        if mode == "check" {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for c in cases.iter_mut() {
                let nc = num_chunks(&c.input);
                match decode_helper(&c.input, nc, c.config, &mut c.out[..]) {
                    Ok(n) => { fnv(&mut h, format!("ok {} ", n).as_bytes()); fnv(&mut h, &c.out[..n]); }
                    Err(e) => fnv(&mut h, format!("err {:?}", e).as_bytes()),
                }
                fnv(&mut h, b"\n");
            }
            println!("\n{{\"cases\": {}, \"output_digest\": \"{:016x}\"}}", cases.len(), h);
        } else {
            let mut acc: u64 = 0;
            let t0 = Instant::now();
            for _ in 0..repeat {
                for c in cases.iter_mut() {
                    let nc = num_chunks(&c.input);
                    match decode_helper(&c.input, nc, c.config, &mut c.out[..]) {
                        Ok(n) => acc = acc.wrapping_add(n as u64).wrapping_add(c.out.get(n / 2).copied().unwrap_or(0) as u64),
                        Err(_) => acc = acc.wrapping_add(7),
                    }
                }
            }
            let el = t0.elapsed().as_secs_f64();
            eprintln!("checksum {}", acc);
            println!("\n{{\"cases\": {}, \"repeat\": {}, \"elapsed_s\": {:.6}}}", cases.len(), repeat, el);
        }
    }
}
