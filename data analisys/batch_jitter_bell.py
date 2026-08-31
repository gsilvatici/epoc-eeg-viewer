import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt, pi, exp

file_path_nowait = 'C:\\Users\\gabri\\Desktop\\pf-anregung\\data analisys\\studies\\device latency nowait\\study_nowait_device_latency_4.csv'
file_path_wait   = 'C:\\Users\\gabri\\Desktop\\pf-anregung\\data analisys\\studies\\device latency wait\\study_wait_device_latency_3.csv'

def load_latencies_ms(csv_path):
    df = pd.read_csv(csv_path, header=None, names=['timestamp', 'marker'])

    # keep only numeric timestamps
    df = df[pd.to_numeric(df['timestamp'], errors='coerce').notnull()].copy()
    df['timestamp'] = pd.to_numeric(df['timestamp'])

    # normalize markers (strip spaces)
    df['marker'] = df['marker'].astype(str).str.strip()

    r_idx = df.index[df['marker'] == 'R'].tolist()
    s_idx = df.index[df['marker'] == 'S'].tolist()

    # for each R, find next S and compute delta (ms)
    diffs = []
    s_iter = iter(s_idx)
    next_s = next(s_iter, None)
    for i in r_idx:
        while next_s is not None and next_s <= i:
            next_s = next(s_iter, None)
        if next_s is not None:
            diffs.append((df.at[next_s, 'timestamp'] - df.at[i, 'timestamp']))
    return np.array(diffs, dtype=float)

def normal_pdf(x, mu, sigma):
    if sigma <= 0:
        return np.zeros_like(x)
    return (1.0/(sigma*sqrt(2*pi))) * np.exp(-0.5*((x - mu)/sigma)**2)

def plot_hist_with_normal(diffs_ms, title, outfile):
    diffs_ms = np.asarray(diffs_ms, dtype=float)
    mu = diffs_ms.mean()
    sigma = diffs_ms.std(ddof=1)

    fig, ax = plt.subplots(figsize=(6, 4))

    # histogram as density so the normal pdf overlays naturally
    n, bins, patches = ax.hist(diffs_ms, bins='auto', density=True, edgecolor='black', alpha=0.6)

    # normal curve over bin range (with a bit of padding)
    x_min = min(diffs_ms.min(), bins.min())
    x_max = max(diffs_ms.max(), bins.max())
    pad = 0.05 * (x_max - x_min if x_max > x_min else 1.0)
    xs = np.linspace(x_min - pad, x_max + pad, 400)
    ax.plot(xs, normal_pdf(xs, mu, sigma), linewidth=2)

    # rug: tiny vertical ticks at each sample to show scatter
    rug_y = (n.max() if len(n) else 1.0) * 0.05
    for v in diffs_ms:
        ax.plot([v, v], [0, rug_y], linewidth=1)

    # annotate stats (mean / std / N)
    text = f'Mean: {mu:.2f} ms\nSTD: {sigma:.2f} ms'
    ax.text(0.98, 0.97, text, transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    ax.set_title(title)
    ax.set_xlabel('Latency (ms)')
    ax.set_ylabel('Density')
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return mu, sigma

def plot_overlay_normals(diffs_a, label_a, diffs_b, label_b, outfile):
    diffs_a = np.asarray(diffs_a, dtype=float)
    diffs_b = np.asarray(diffs_b, dtype=float)

    mu_a, sd_a = diffs_a.mean(), diffs_a.std(ddof=1)
    mu_b, sd_b = diffs_b.mean(), diffs_b.std(ddof=1)

    x_min = min(diffs_a.min(), diffs_b.min())
    x_max = max(diffs_a.max(), diffs_b.max())
    pad = 0.1 * (x_max - x_min if x_max > x_min else 1.0)
    xs = np.linspace(x_min - pad, x_max + pad, 500)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(xs, normal_pdf(xs, mu_a, sd_a), linewidth=2, label=f'{label_a} (Mean={mu_a:.2f}, STD={sd_a:.2f})')
    ax.plot(xs, normal_pdf(xs, mu_b, sd_b), linewidth=2, linestyle='--', label=f'{label_b} (Mean={mu_b:.2f}, STD={sd_b:.2f})')

    ax.set_title('Latency distributions (Normal fits)')
    ax.set_xlabel('Latency (ms)')
    ax.set_ylabel('Density')
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close(fig)

# -----------------------------
# 3) run
# -----------------------------
nowait = load_latencies_ms(file_path_nowait)
wait   = load_latencies_ms(file_path_wait)

mu0, sd0 = plot_hist_with_normal(nowait, 'Sync response time (no sleep)', 'SyncLatency_Normal_NoSleep.png')
mu1, sd1 = plot_hist_with_normal(wait,   'Sync response time (with sleep)', 'SyncLatency_Normal_Sleep.png')

# optional: overlay the two fitted normals in one figure
plot_overlay_normals(nowait, 'No sleep', wait, 'With sleep', 'SyncLatency_Normal_Overlay.png')

# print summary in console
print('No sleep  -> N = {}, Mean = {:.2f} ms, STD = {:.2f} ms'.format(len(nowait), mu0, sd0))
print('With sleep-> N = {}, Mean = {:.2f} ms, STD = {:.2f} ms'.format(len(wait),   mu1, sd1))
