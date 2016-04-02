The data is collected using:

~~~sh
cargo run --release
~~~

and

~~~sh
clang++ -std=c++11 -O3 bench.cpp -lsqlite3 && ./a.out
~~~

Miscellaneous info:

~~~
$ uname -a
Linux … 4.4.5-1-ARCH #1 SMP PREEMPT Thu Mar 10 07:38:19 CET 2016 x86_64 GNU/Linux
Intel(R) Core(TM) i5-2500K CPU @ 3.30GHz

$ lscpu
Model name:            Intel(R) Core(TM) i5-2500K CPU @ 3.30GHz
CPU MHz:               2603.906
CPU max MHz:           5900.0000
CPU min MHz:           1600.0000
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              6144K

$ clang --version
clang version 3.7.1 (tags/RELEASE_371/final)
Target: x86_64-unknown-linux-gnu
Thread model: posix

$ rustc --version
rustc 1.7.0

$ cat Cargo.lock 
[root]
name = "bench-maps"
version = "0.1.0"
dependencies = [
 "rand 0.3.14 (registry+https://github.com/rust-lang/crates.io-index)",
 "time 0.1.35 (registry+https://github.com/rust-lang/crates.io-index)",
]

[[package]]
name = "kernel32-sys"
version = "0.2.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
dependencies = [
 "winapi 0.2.6 (registry+https://github.com/rust-lang/crates.io-index)",
 "winapi-build 0.1.1 (registry+https://github.com/rust-lang/crates.io-index)",
]

[[package]]
name = "libc"
version = "0.2.9"
source = "registry+https://github.com/rust-lang/crates.io-index"

[[package]]
name = "rand"
version = "0.3.14"
source = "registry+https://github.com/rust-lang/crates.io-index"
dependencies = [
 "libc 0.2.9 (registry+https://github.com/rust-lang/crates.io-index)",
]

[[package]]
name = "time"
version = "0.1.35"
source = "registry+https://github.com/rust-lang/crates.io-index"
dependencies = [
 "kernel32-sys 0.2.1 (registry+https://github.com/rust-lang/crates.io-index)",
 "libc 0.2.9 (registry+https://github.com/rust-lang/crates.io-index)",
 "winapi 0.2.6 (registry+https://github.com/rust-lang/crates.io-index)",
]

[[package]]
name = "winapi"
version = "0.2.6"
source = "registry+https://github.com/rust-lang/crates.io-index"

[[package]]
name = "winapi-build"
version = "0.1.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
~~~
