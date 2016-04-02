extern crate time;
extern crate rand;

use rand::Rng;
use time::precise_time_ns;
use std::collections::{BTreeMap, HashMap};

fn main() {

    let mut rng = rand::thread_rng();

    let nimax = 25;

    for ni in 0 .. nimax {
        let n = 1 << ni;
        let t = precise_time_ns();
        let mut m = BTreeMap::new();
        for _ in 0..n {
            let r:i64 = rng.gen();
            let key = r % 2147483647;
            m.insert(key, 1);
            let _ = m.remove(&key);
        }
        let t = (precise_time_ns() - t) as f64 / n as f64;
        println!("{}\t{}", n, t);
    }

    for ni in 0 .. nimax {
        let n = 1 << ni;
        let mut m = HashMap::new();
        let t = precise_time_ns();
        for _ in 0..n {
            let r:i64 = rng.gen();
            let key = r % 2147483647;
            m.insert(key, 1);
            let _ = m.remove(&key);
        }
        let t = (precise_time_ns() - t) as f64 / n as f64;
        println!("{}\t{}", n, t);
    }
}
