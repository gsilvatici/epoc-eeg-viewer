"""Round-trip distribution of the sync command, with and without the
per-sample pacing sleep. Produces SyncQuantization.png for the thesis."""
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FS, NSAMP = 128.0, 4
TS = 1000.0 / FS                      # 7.8125 ms per sample


def round_trips(folder):
    """R = sync issued, S = first marked sample read back (host clock, ms)."""
    out = []
    for fp in sorted(glob.glob(folder + "/*.csv")):
        df = pd.read_csv(fp, header=None, names=["timestamp", "marker"],
                         usecols=[0, 1], on_bad_lines="skip")
        df = df[pd.to_numeric(df["timestamp"], errors="coerce").notnull()]
        df["timestamp"] = pd.to_numeric(df["timestamp"])
        r_idx = df.index[df["marker"] == " R"].tolist()
        s_idx = df.index[df["marker"] == " S"].tolist()
        for r in r_idx:
            s = next((x for x in s_idx if x > r), None)
            if s is not None:
                out.append(df.at[s, "timestamp"] - df.at[r, "timestamp"])
    return np.array(out, dtype=float)


nowait = round_trips("studies/device latency nowait")
wait = round_trips("studies/device latency wait")

bins = np.arange(5, 36)
h_nw = np.array([(nowait == b).sum() for b in bins]) / len(nowait) * 100
h_w = np.array([(wait == b).sum() for b in bins]) / len(wait) * 100

fig, ax = plt.subplots(figsize=(7.2, 3.4))

# batch-completion grid: k whole sample periods
for k in range(1, NSAMP + 1):
    ax.axvline(k * TS, color="0.55", ls=(0, (4, 3)), lw=1.0, zorder=1)
    near = np.abs(bins - k * TS) <= 4
    ax.text(k * TS, h_nw[near].max() + 2.0, f"$k={k}$", ha="center", va="bottom",
            fontsize=10, color="0.35")

ax.bar(bins, h_nw, width=0.75, color="#1f77b4", edgecolor="white",
       linewidth=0.4, zorder=3)

ax.set_xlabel("Sync round trip (ms)", fontsize=11)
ax.set_ylabel("Events (%)", fontsize=11)
ax.set_xlim(5, 35)
ax.set_ylim(0, 33)
ax.set_xticks([5, 10, 15, 20, 25, 30, 35])
ax.grid(True, axis="y", color="0.9", lw=0.8, zorder=0)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color("0.6")
ax.tick_params(colors="0.3", labelsize=10)

fig.tight_layout()
fig.savefig("SyncQuantization.png", dpi=300, bbox_inches="tight")

print(f"nowait N={len(nowait)} mean={nowait.mean():.2f} sd={nowait.std(ddof=1):.2f} min={nowait.min():.0f}")
print(f"wait   N={len(wait)} mean={wait.mean():.2f} sd={wait.std(ddof=1):.2f} min={wait.min():.0f}")
print("grid k*7.8125 =", [round(k * TS, 2) for k in range(1, 5)])

# --- residual after removing the batch contribution (quoted in the thesis) ---
k = np.round(nowait / TS).astype(int)
res = nowait - k * TS
print(f"residual all: {res.mean():+.2f} +/- {res.std(ddof=1):.2f} ms (N={len(res)})")
for kk in range(1, NSAMP + 1):
    r = res[k == kk]
    print(f"  k={kk}: n={len(r):3d}  {r.mean():+.2f} +/- {r.std(ddof=1):.2f} ms")
