import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

def analyze_data_from_csv(csv_file):
    # Read the data
    data = pd.read_csv(csv_file, header=None, names=['timestamp', 'signal', 'stimuli'], usecols=[0, 1, 2])
    # ... (existing data processing code)


    data['ticks'] = range(len(data))
    data['timestamp'] = data['timestamp']
    ticks = data['ticks'].values
    raw_signal = data['signal'].values

    # Get the ticks where "stimuli" occurs in the third column
    latency_ticks = data[pd.notna(data['stimuli']) & (data['stimuli'] != '')]['ticks'].values

    # Set the parameters
    sampling_freq = 128
    target_freq = 16
    tolerance = 256

    # Analyze the raw signal using the sliding window method, 1 sample at a time
    window_size = sampling_freq
    step_size = 1

    detected_windows = []

    for latency_timestamp in latency_ticks:
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
            goertzel_results.append((goertzel_result, ticks[i]))
            if (diff > 0):
                diff_results.append((diff, ticks[i]))        
            diff = last_goertzel - goertzel_result
            last_goertzel = goertzel_result

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


    # lags = detected_windows - latency_ticks
    lags = data['timestamp'].iloc[detected_windows].values - data['timestamp'].iloc[latency_ticks].values
    print (lags)
    np.random.shuffle(lags)

    # Return the lags and their corresponding event indices
    return np.arange(len(lags)), lags

def plot_latency(x, y, color, label_prefix):
    mu = np.mean(y)
    std = np.std(y)
    upperBound = mu + std
    lowerBound = mu - std
    dif = upperBound - lowerBound

    plt.plot(x, y, '-', color=color, label=f'{label_prefix} (Mean: {mu:.2f} ms, ±{dif:.2f} ms)')

    # textstr = f"Mean: {mu:.2f} ms ±: {dif:.2f} ms"
    # props = dict(boxstyle='round', facecolor=color, alpha=0.5)
    # plt.text(0.01, 0.99, textstr, transform=plt.gca().transAxes, fontsize=12,
    #          verticalalignment='top', bbox=props)

# Process the first CSV file
x1, y1 = analyze_data_from_csv('C:\\Users\\gabri\\Desktop\\BCI\\epoceeg-master\\study_wait_wasapi_3.csv')
# Process the second CSV file
x2, y2 = analyze_data_from_csv('C:\\Users\\gabri\\Desktop\\BCI\\epoceeg-master\\study_wait_wasapi_500ms_3.csv')

# Now plot both sets of lags on the same plot
plot_latency(x1, y1, 'skyblue', 'WASAPI')
plot_latency(x2, y2, 'orange', 'WASAPI with 500ms delay')

# Customize the plot
plt.title("Delay Comparison", fontsize=16)
plt.xlabel("Event Count", fontsize=14)
plt.ylabel("Time Difference (ms)", fontsize=14)
plt.legend(loc='upper right')

plt.grid(True)
plt.ylim(90, 800)
plt.xlim(0, 100)

# Save the plot with a high resolution
plt.savefig('LatencyCompareDelay.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()


