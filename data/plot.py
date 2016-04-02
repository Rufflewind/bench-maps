#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

def plot_data(ax, name, filename):
    table = np.loadtxt(filename)
    ns = table[:, 0]
    ts = table[:, 1]
    ax.plot(ns, ts, label=name)

fig, ax = plt.subplots()
plot_data(ax, "C++ ordered_map", "cpp_ord_ins.txt")
plot_data(ax, "C++ unordered_map", "cpp_unord_ins.txt")
plot_data(ax, "Rust BTreeMap", "rs_btree_ins.txt")
plot_data(ax, "Rust HashMap", "rs_hash_ins.txt")
ax.set_xlim(64, 16777216)
ax.set_ylim(0, 1250)
ax.set_xlabel("number of inserts")
ax.set_ylabel("time per insert /ns")
ax.set_xscale("log")
ax.grid("on")
legend = ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
fig.tight_layout()
fig.savefig("plot.png",
            bbox_extra_artists=(legend,),
            bbox_inches="tight")
