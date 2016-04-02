# Map benchmarks for C++ and Rust

Some quick and dirty benchmarks of various map (associative array)
implementations in C++ and Rust.

Included are:

  - C++'s `ordered_map` implemented using red-black trees.
  - C++'s `unordered_map` implemented using hash tables.
  - Rust's `BTreeMap` implemented using B-trees.
  - Rust's `HashMap` implemented using hash tables.

The benchmarks plot the average time taken per insert against the total number
of elements inserted.  For tree maps, logarithmic complexity is
expected, so on the semilogx plot it should appear as a rising straight line.
For hash maps, the constant complexity is expected, so it should
appear as a flat horizontal line.

Here is some [actual data](data):

![Plot of average time taken per insert in nanoseconds against the total
  number of elements inserted.](data/plot.png)

In reality, it's not quite so simple.  For tree maps, there seems to be a
baseline overhead of around 100 ns.  Above a certain number of elements, the
logarithmic behavior surpasses the baseline overhead.  For hash maps, the time
taken does increase slightly as the number of elements increases.

This is probably due to the hashtable resizing, which occurs rather frequently
in the tests since the number of elements is doubled each time.  In a more
realistic situation where the resizes are infrequent, this would not be as
bad.

The data for fewer than 64 elements are not included as the results are not
very accurate and probably inflated due to overhead.

I was originally going to compare against SQLite3 as well, but it's like an
order of magnitude slower so not really worth it.  The SQLite code is still
left in the source code though.

If you see any errors in the code or have any suggestions that can improve the
quality of the results, feel free to submit a bug report or pull request!

Known limitations:

  - Rust and C++ use different random number generators (RNGs).
  - The time needed to generate a RNG might not insignificant.
