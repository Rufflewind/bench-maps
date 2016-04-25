# Map benchmarks for C++ and Rust

Benchmarks for:

  - C++'s `ordered_map` implemented using red-black trees.
  - C++'s `unordered_map` implemented using hash tables.
  - Rust's `BTreeMap` implemented using B-trees.
  - Rust's `HashMap` implemented using hash tables.

For tree maps, logarithmic complexity is expected, so on the semilogx plot it
should appear as a rising straight line.  For hash maps, the constant
complexity is expected, so it should appear as a flat horizontal line.

Here is some [actual data](data):

![Plot of average time taken per lookup in nanoseconds against the total
  number of elements inserted.](data/plot-lookup.png)

![Plot of average time taken per insert in nanoseconds against the total
  number of elements inserted.](data/plot-insert.png)

## Summary

  - `BTreeMap` is remarkably good and competitive with `HashMap` until about a
    size of a thousand.
  - `unordered_map` is good and on par with `HashMap`.
  - `map` (RB-tree) is quite mediocre.

## Technical details

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

## Why did I do this?

There's remarkably little information on the efficiency of C++ and Rust's
associative arrays, so I figured I could perform some benchmarks of my own.

Turns out, it's a bit more complicated than I imagined.  Insertions are tricky
because they change the size of the map, yet the performance of a map is very
size-dependent.  But a single insertion doesn't take much time at all, so
measuring only one would lead to a lot of noise and overhead in the data.  I
ended up taking a balanced approach and did a some of binning to reduce the
noise without completely smearing out the data.

I wanted to avoid "predictable" inputs (to avoid cache and branch prediction
effects), so I used a RNG to generate the keys.  However, the overhead of a
RNG is not exactly negligible (costs 10-20ns) in comparison to a single lookup
on a small map, so that needed to be subtracted off.

Lastly, I also needed to make sure the results of lookups are be consumed
somehow, otherwise the compiler might optimize out the load from memory.  To
mitigate this I did a dummy operation: the result of each lookup is added to a
running total, and the total is printed at the very end.
