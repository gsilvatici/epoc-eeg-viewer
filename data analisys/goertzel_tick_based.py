import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from scipy.stats import norm

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

# Load data from 'raw_data1.csv'
data = pd.read_csv('studies/signal_registry_gs0.csv', header=None, names=['timestamp', 'signal', 'stimuli'], usecols=[0, 1, 2])

timestamps = data['timestamp'].values
raw_signal = data['signal'].values


# Get the timestamps where "stimuli" occurs in the third column
latency_timestamps = data[pd.notna(data['stimuli']) & (data['stimuli'] != '')]['timestamp'].values

# Set the parameters
sampling_freq = 128
target_freq = 16
tolerance = 256

# Analyze the raw signal using the sliding window method, 1 sample at a time
window_size = sampling_freq
step_size = int(window_size / 128)

detected_windows = []

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Apply band-pass filter around 16Hz
# raw_signal = butter_bandpass_filter(raw_signal, 14, 18, sampling_freq)



for latency_timestamp in latency_timestamps:
    # Define the search range based on the tolerance
    start_index = max(0, latency_timestamp)
    end_index = min(len(raw_signal) - window_size, latency_timestamp + tolerance)

    last_goertzel = 0
    goertzel_results = []
    diff_results = []
    diff = 0

    for i in range(start_index, end_index, step_size):
        window = raw_signal[i:i + window_size]

        goertzel_result = goertzel(window, target_freq, sampling_freq)
        goertzel_results.append((goertzel_result, timestamps[i]))
        if (diff > 0):
            diff_results.append((diff, timestamps[i]))        
        diff = last_goertzel - goertzel_result
        last_goertzel = goertzel_result

    # # Find the tuple with the maximum Goertzel result\
    # max_diff_result_tuple = max(diff_results, key=lambda x: x[0])
    # # Get the timestamp corresponding to the maximum Goertzel result\
    # max_diff_result_timestamp = max_diff_result_tuple[1]
    # detected_windows.append(max_diff_result_timestamp)
    # Implement dynamic thresholding
    all_goertzel_values = [x[0] for x in goertzel_results]
    mean_goertzel = np.mean(all_goertzel_values)
    std_goertzel = np.std(all_goertzel_values)
    threshold_multiplier = 1  # Adjust based on needs
    threshold = mean_goertzel + threshold_multiplier * std_goertzel
    filtered_goertzel_results = [(value, timestamp) for value, timestamp in goertzel_results if value > threshold]

    # Find the tuple with the maximum Goertzel result
    if filtered_goertzel_results:
        max_diff_result_tuple = max(filtered_goertzel_results, key=lambda x: x[0])
        max_diff_result_timestamp = max_diff_result_tuple[1]
        detected_windows.append(max_diff_result_timestamp)


lags = detected_windows - latency_timestamps

print (lags)

# Calculate the mean (mu) and standard deviation (std)
mu, std = np.mean(lags), np.std(lags)

plt.hist(lags, bins=30, density=True, alpha=0.6, color='g')

xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2, label="N({:.2f},{:.2f})".format(mu, std))

title = "Fit results: mu = {:.2f},  std = {:.2f}".format(mu, std)
plt.title(title)
plt.legend()

plt.show()