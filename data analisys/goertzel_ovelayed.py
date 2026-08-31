import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# === Common axes / bins ===
X_MIN, X_MAX = 105, 175
Y_MIN, Y_MAX = 0, 0.30
BIN_EDGES = np.linspace(X_MIN, X_MAX, 31)  # 30 bins

# === Input files ===
WASAPI_PATH = r'C:\Users\gabri\Desktop\pf-anregung\data analisys\studies\wasapi wait\study_wait_wasapi_3.csv'
DSOUND_PATH = r'C:\Users\gabri\Desktop\pf-anregung\data analisys\studies\study_wait_dsound_curated.csv'

def goertzel(samples, target_freq, sampling_freq):
    normalized_target_freq = target_freq * 2 * np.pi / sampling_freq
    coeff = 2 * np.cos(normalized_target_freq)
    s_prev = 0
    s_prev2 = 0
    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    return s_prev2 ** 2 + s_prev ** 2 - coeff * s_prev * s_prev2

def compute_lags(csv_path):
    data = pd.read_csv(csv_path, header=None, names=['timestamp', 'signal', 'stimuli'], usecols=[0, 1, 2])
    data['ticks'] = range(len(data))
    ticks = data['ticks'].values
    raw_signal = data['signal'].values
    latency_ticks = data[pd.notna(data['stimuli']) & (data['stimuli'] != '')]['ticks'].values

    sampling_freq = 128
    target_freq = 16
    tolerance = 256
    window_size = sampling_freq
    step_size = 1

    detected_windows = []
    for latency_timestamp in latency_ticks:
        start_index = max(0, latency_timestamp)
        end_index = min(len(raw_signal) - window_size, latency_timestamp + tolerance)

        last_goertzel = 0
        goertzel_results = []
        for i in range(start_index, end_index, step_size):
            window = raw_signal[i:i + window_size]
            g = goertzel(window, target_freq, sampling_freq)
            goertzel_results.append((g, ticks[i]))
            last_goertzel = g

        all_vals = [x[0] for x in goertzel_results]
        thr = np.mean(all_vals) + 1 * np.std(all_vals)
        filt = [(v, t) for v, t in goertzel_results if v > thr]
        if filt:
            max_t = max(filt, key=lambda x: x[0])[1]
            detected_windows.append(max_t)

    lags = data['timestamp'].iloc[detected_windows].values - data['timestamp'].iloc[latency_ticks].values
    return lags

# --- compute both ---
lags_w = compute_lags(WASAPI_PATH)
lags_d = compute_lags(DSOUND_PATH)

mu_w, std_w = np.mean(lags_w), np.std(lags_w)
mu_d, std_d = np.mean(lags_d), np.std(lags_d)

# --- plot both on the same axes ---
plt.figure(figsize=(8, 5))

# Histograms
# plt.hist(lags_w, bins=BIN_EDGES, density=True, alpha=0.35, edgecolor='none',
#          label='WASAPI', color='tab:blue')
# plt.hist(lags_d, bins=BIN_EDGES, density=True, alpha=0.35, edgecolor='none',
#          label='DirectSound', color='tab:orange')

plt.hist(lags_w, bins=BIN_EDGES, density=True, alpha=0.35, edgecolor='none', color='tab:blue')
plt.hist(lags_d, bins=BIN_EDGES, density=True, alpha=0.35, edgecolor='none', color='tab:orange')


# Gaussian fits
x = np.linspace(X_MIN, X_MAX, 400)
plt.plot(x, norm.pdf(x, mu_w, std_w), linewidth=2, color='tab:blue',
         label=f'WASAPI Mean={mu_w:.2f} ms, STD={std_w:.2f} ms')
plt.plot(x, norm.pdf(x, mu_d, std_d), linewidth=2, color='tab:orange',
         label=f'DirectSound Mean={mu_d:.2f} ms, STD={std_d:.2f} ms')

# Axes and labels
plt.xlim(X_MIN, X_MAX)
plt.ylim(Y_MIN, Y_MAX)  # <= max Y = 0.40 as requested
plt.title('Latency distributions: WASAPI vs DirectSound')
plt.xlabel('Time Difference (ms)')
plt.legend()
plt.tight_layout()
plt.savefig('LatencyOverlayed.png', dpi=300, bbox_inches='tight')
plt.show()
