#!/usr/bin/env python
#
# we assume the lookup/insert time depends on:
#
#   - whether it was a hit or miss
#   - number of elements in the array prior to the operation
#
# we could model the time as a simple sum:
#
#     num_hits * time_hit(num_elems) + num_misses * time_miss(num_elems)
#
# and then do a fit to obtain time_hit and time_miss, but this sometimes gives
# us negative results because of the noise in the data.
#
# to avoid this, we simply discard all data except those that have num_misses
# = 0 or num_hits = 0.  wasteful, sure, but it's not too bad as long as we
# keep repeats small
#
import base64, glob, hashlib, json, os, re, sys, subprocess, tempfile
import numpy as np
import matplotlib.pyplot as plt

#@snip/hash_file[
def hash_file(hasher, file, block_size=(1 << 20)):
    if isinstance(file, str):
        with open(file, "rb") as f:
            return hash_file(hasher, f, block_size=block_size)
    h = hasher()
    for block in iter(lambda: file.read(block_size), b""):
        h.update(block)
    return h
#@]

def get_or_insert(d, k, fdefault):
    try:
        return d[k]
    except KeyError:
        pass
    x = fdefault()
    d[k] = x
    return x

def parse_json(s):
    '''Allows "//" at beginning of lines to be used for comments.'''
    return json.loads("".join(line for line in s.split("\n")
                              if not re.match(r"\s*//", line)))

def find_next_lowest(xs, x):
    '''Do a binary search to find the index of the largest number in `xs` that
    is not greater than `x`.  Returns `-1` if there isn't any.'''
    left = 0
    right = len(xs) - 1
    while True:
        mid = (left + right) // 2
        if x == xs[mid]:
            return mid
        elif x > xs[mid]:
            left = mid + 1
            if left > right:
                return mid
        else:
            right = mid - 1
            if left > right:
                return mid - 1

def bin_to(bins, x):
    '''Find the appropriate bin for `x`.  `None` if outside the range.  `bins`
    is a sorted array of bins starting from the lower bound to the upper
    bound.'''
    i = find_next_lowest(bins, x)
    if i < 0 or i == len(bins) - 1:
        return
    return i

def jsonify(j):
    if isinstance(j, dict):
        return dict((str(k), jsonify(v)) for k, v in j.items())
    elif isinstance(j, list) or isinstance(j, tuple):
        return [jsonify(v) for v in j]
    elif isinstance(j, str):
        return str(j)
    elif isinstance(j, float):
        return float(j)
    elif isinstance(j, int) or isinstance(j, np.int64):
        return int(j)
    raise ValueError("unknown value: {0} (type: {1})"
                     .format(repr(j), type(j)))

def logrange(x, y, n=50):
    return np.logspace(np.log10(x), np.log10(y), n)

def dataframe_from_rows(rows):
    return pd.DataFrame.from_records(rows[1:], columns=rows[0])

def drop_outliers(d, factor):
    return d[~((d - d.mean()).abs() > factor * d.std())]

def bench(program, nmax, repeats, count):
    s = subprocess.check_output([program, str(nmax),
                                 str(repeats), str(count)],
                                universal_newlines=True)
    j = parse_json(s)
    times = {}
    rng_times = []
    for method, operation_data in j.items():
        if method.startswith("_"):
            continue
        rng_times.extend(x[0] for x in operation_data["rng"][1:])
        method_times = {}
        times[method] = method_times

        operation_sizes = []
        operation_hitss = []
        operation_missess = []
        operation_times = []
        method_times["insert"] = {
            "size": operation_sizes,
            "hits": operation_hitss,
            "misses": operation_missess,
            "time": operation_times,
        }
        last_size = 0
        for _, size, time in operation_data["insert"][1:]:
            misses = size - last_size
            hits = repeats - misses
            avg_size = (size + last_size) // 2
            last_size = size
            if misses and hits:
                continue
            operation_sizes.append(avg_size)
            operation_hitss.append(hits)
            operation_missess.append(misses)
            operation_times.append(time)

        operation_sizes = []
        operation_hitss = []
        operation_missess = []
        operation_times = []
        method_times["lookup"] = {
            "size": operation_sizes,
            "hits": operation_hitss,
            "misses": operation_missess,
            "time": operation_times,
        }
        for _, misses, time in operation_data["lookup"][1:]:
            hits = repeats - misses
            if misses and hits:
                continue
            operation_sizes.append(size)
            operation_hitss.append(hits)
            operation_missess.append(misses)
            operation_times.append(time)

    return {
        "lang": j["_lang"],
        "nmax": nmax,
        "repeats": repeats,
        "rng_times": rng_times,
        "count": count,
        "times": times,
    }

def main_bench(program):
    REPEATS = 3 # don't make this too big or most data will get discarded
    NMAX_MIN = 16
    NMAX_MAX = 500000
    NMAX_COUNT = 100

    nmaxs = list(map(int, logrange(NMAX_MIN, NMAX_MAX, NMAX_COUNT)))
    print("nmaxs:", nmaxs)
    for nmax in nmaxs:
        repeats = REPEATS
        print("nmax: ", nmax)
        # TODO: find the optimal 'count' that gives us 0.5 lookup hit chance
        for count in map(int, logrange(nmax / repeats * .5,
                                       nmax / repeats * 2, 4)):
            try:
                os.mkdir("raw_data")
            except OSError:
                pass
            with tempfile.NamedTemporaryFile(
                    mode="w",
                    dir="raw_data",
                    suffix=".tmp",
                    delete=False) as f:
                json.dump(bench(program, nmax, repeats, count), f, sort_keys=True)
                tmpfn = f.name
            h = hash_file(hashlib.md5, tmpfn).digest()
            h = base64.urlsafe_b64encode(h).decode("ascii").rstrip("=")
            fn = ("raw_data/{0}_{1}_{2}_{3}.json"
                  .format(nmax, repeats, count, h))
            os.rename(f.name, fn)

def main_analyze():
    # minimum number of measurements needed
    # otherwise we don't include it
    MIN_COUNT = 8
    SIZE_MIN = 8
    SIZE_MAX = 500000
    NUM_BINS = 100
    SIZE_BINS = np.array(sorted(set(map(int, logrange(SIZE_MIN, SIZE_MAX, NUM_BINS)))))
    print("SIZE_BINS:", SIZE_BINS)

    size_bins = SIZE_BINS
    # operation -> method -> binned times
    # (binned times by method by operation)
    btbmbo = {}
    rng_times = {"cpp": [], "rs": []}
    def mkbt():
        return [{
            "time_hit": [],
            "time_miss": [],
        } for _ in range(len(size_bins))]
    for fn in glob.glob("raw_data/*.json"):
        with open(fn) as f:
            j = json.load(f)
        lang = j.get("lang", "cpp" if "map" in j["times"] else "rs")
        rng_times[lang].extend(np.array(j["rng_times"]) / j["repeats"])
        for method, times_by_operation in j["times"].items():
            for operation, times in times_by_operation.items():
                btbm = get_or_insert(btbmbo, operation, lambda: {})
                binned_times = get_or_insert(btbm, method, mkbt)
                for size, hits, misses, time in zip(times["size"],
                                                    times["hits"],
                                                    times["misses"],
                                                    times["time"]):
                    assert not (hits and misses)
                    assert hits or misses
                    bin_i = bin_to(size_bins, size)
                    if not bin_i:
                        continue
                    if hits:
                        binned_times[bin_i]["time_hit"].append(time / hits)
                    else:
                        binned_times[bin_i]["time_miss"].append(time / misses)

    t = {
        "operation": [],
        "method": [],
        "size": [],
        "is_hit": [],
        "time": [],
        "time_min": [],
        "time_stdev": [],
        "time_sdom": [],
    }
    for operation, btbm in btbmbo.items():
        for method, binned_times in btbm.items():
            for sizel, sizeu, times in zip(size_bins,
                                           size_bins[1:],
                                           binned_times):
                size = (sizel + sizeu) // 2
                for is_hit, times in [(True, times["time_hit"]),
                                     (False, times["time_miss"])]:
                    if len(times) < MIN_COUNT:
                        continue
                    t["operation"].append(operation)
                    t["method"].append(method)
                    t["size"].append(size)
                    t["is_hit"].append(is_hit)
                    t["time"].append(np.mean(times))
                    t["time_min"].append(np.min(times))
                    t["time_stdev"].append(np.std(times))
                    t["time_sdom"].append(t["time_stdev"][-1] /
                                          np.sqrt(len(times)))

    with open("analysis.json", "w") as f:
        json.dump(jsonify({
            "data": t,
            "t_rng": dict((lang, {
                "mean": np.mean(t),
                "min": np.min(t),
                "stdev": np.std(t),
                "sdom": np.std(t) / np.sqrt(len(t)),
            }) for lang, t in rng_times.items())
        }), f)

def main_plot():
    import pandas as pd
    PLOT_MIN = True # min vs mean
    SUBTRACT_RNG = True
    ERR_BARS = True
    LOG_Y = False
    T_RNG_FIELD = "mean"
    COLORS = {
        "BTreeMap": "#e91e63",
        "HashMap": "#f29312",
        "map": "#4caf50",
        "unordered_map": "#2196f3",
    }
    RNGCOLORS = {
        "rs": "#f29312",
        "cpp": "#2196f3",
    }
    with open("analysis.json") as f:
        j = json.load(f)
    for lang, r in j["t_rng"].items():
        print("t_rng[{0}] = {1} +/- {2} (stdev: {3}, min: {4})"
              .format(lang, r["mean"], r["sdom"], r["stdev"], r["min"]))
    t = pd.DataFrame.from_records(j["data"])
    j["t_rng"] = dict((lang, dict((k, v * 1e9) for k, v in r.items()))
                      for lang, r in j["t_rng"].items())
    t["time"] = t["time"] * 1e9
    t["time_min"] = t["time_min"] * 1e9
    t["time_stdev"] = t["time_stdev"] * 1e9
    t["time_sdom"] = t["time_sdom"] * 1e9
    fkwargs = lambda gg: {}
    time_field = "time"
    if PLOT_MIN:
        time_field = "time_min"
        ERR_BARS = False
    method_to_lang = {
        "map": "cpp",
        "unordered_map": "cpp",
        "BTreeMap": "rs",
        "HashMap": "rs",
    }
    if SUBTRACT_RNG:
        def get_time(t, method):
            return t - j["t_rng"][method_to_lang[method]][T_RNG_FIELD]
    else:
        def get_time(t, method):
            return t
    for operation, d in t.groupby(["operation"]):
        fig, ax = plt.subplots()
        for method, g in d.groupby(["method"]):
            for is_hit, gg in g.groupby(["is_hit"]):
                labels = {True: "hit", False: "miss"}
                linestyles = {True: "-", False: "--"}
                if ERR_BARS:
                    ax.fill_between(
                        gg["size"],
                        get_time(gg[time_field], method) - gg["time_sdom"],
                        get_time(gg[time_field], method) + gg["time_sdom"],
                        color=COLORS[method],
                        linewidth=0,
                        alpha=.2,
                    )
                    ax.fill_between(
                        gg["size"],
                        get_time(gg[time_field], method) - .5 * gg["time_sdom"],
                        get_time(gg[time_field], method) + .5 * gg["time_sdom"],
                        color=COLORS[method],
                        linewidth=0,
                        alpha=.2,
                    )
                ax.plot(
                    gg["size"],
                    get_time(gg[time_field], method),
                    label="{0}-{1}".format(method, labels[is_hit]),
                    linestyle=linestyles[is_hit],
                    linewidth=1.5,
                    alpha=.7,
                    color=COLORS[method],
                )
        if not SUBTRACT_RNG:
            for lang, r in j["t_rng"].items():
                ax.axhline(r[T_RNG_FIELD],
                           label="rng:" + lang,
                           linestyle=":",
                           color=RNGCOLORS[lang])
        ax.set_xlim(min(d["size"]), max(d["size"]))
        if not LOG_Y:
            ax.set_ylim(0, d["time"].quantile(.95) * 1.5)
        ax.set_xlabel("size")
        ax.set_ylabel("time per {0} /ns".format(operation))
        ax.set_xscale("log")
        if LOG_Y:
            ax.set_yscale("log")
        ax.grid("on")
        legend = ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        fig.tight_layout()
        try:
            os.mkdir("plots")
        except OSError:
            pass
        fig.savefig("plots/plot-{0}.svg".format(operation),
                    bbox_extra_artists=(legend,),
                    bbox_inches="tight")

if __name__ == "__main__":
    locals()["main_" + sys.argv[1]](*sys.argv[2:])
