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

![Plot of average time taken per lookup in nanoseconds against the total
  number of elements inserted.](data/plot-lookup.png)

![Plot of average time taken per insert in nanoseconds against the total
  number of elements inserted.](data/plot-insert.png)

"Hits" occur when the lookup succeeds, or when the insertion replaces an
existing item.  "Misses" occur the lookup fails, or when the insertion adds a
new element.

The data has been binned and averaged along the size axis to reduce the noise.
However, this means that local variations are somewhat suppressed.  This
wouldn't be a too bad if the time was actually a smooth function of size, but
in reality that's not the case (notice the spikes), so we try to keep the bin
relatively small.

The cost due to the random number generator (a few tens of nanoseconds) has
been subtracted off.  The shaded region denotes the uncertainty: the lightly
shaded region shows plus or minus the standard deviation of the mean, while
the the darker region shows plus or minus half of that.

The huge periodic spikes are the result of the hash table getting filled up
and thus causing a resize, which causes all the elements to be copied.  In
contrast, trees generally do not have this behavior (except in a few rare
places, for reasons unknown).

If you see any errors in the code or have any suggestions that can improve the
quality of the results, feel free to submit a bug report or pull request!
