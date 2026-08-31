import pandas as pd
import matplotlib.pyplot as plt

file_path = 'C:\\Users\\gabri\\Desktop\\pf-anregung\\data analisys\\studies\\device latency nowait\\study_nowait_device_latency_4.csv'
# file_path = 'C:\\Users\\gabri\\Desktop\\pf-anregung\\data analisys\\studies\\device latency wait\\study_wait_device_latency_3.csv'

# Read the CSV file, assuming there are no headers and the markers are in the second column
df = pd.read_csv(file_path, header=None, names=['timestamp', 'marker'])

# Drop rows where the timestamp is NaN or cannot be converted to numeric
df = df[pd.to_numeric(df['timestamp'], errors='coerce').notnull()]
df['timestamp'] = pd.to_numeric(df['timestamp'])

# Find all the indices of 'R' and 'S'
r_indices = df.index[df['marker'] == ' R'].tolist()
s_indices = df.index[df['marker'] == ' S'].tolist()
# print(r_indices)
# print(s_indices)

# Calculate the differences
differences = []
for r_index in r_indices:
    # Find the next 'S' index that is greater than the 'R' index
    next_s_index = next((s_index for s_index in s_indices if s_index > r_index), None)
    # If there is a following 'S', calculate the difference
    if next_s_index is not None:
        time_difference = df.at[next_s_index, 'timestamp'] - df.at[r_index, 'timestamp']
        differences.append(time_difference)

# Convert differences to a Pandas Series
diff_series = pd.Series(differences)

# Calculate the mean and standard deviation of the differences
mean_diff = diff_series.mean()
std_diff = diff_series.std()

# Plot the data without error bars, using a lighter shade of blue
plt.plot(diff_series.index, diff_series, color='skyblue')

# Set the plot title and labels
# plt.title('Sync response time with sleep', fontsize=16)
plt.title('Sync response time', fontsize=16)
plt.xlabel('Sync count', fontsize=14)
plt.ylabel('Time difference (ms)', fontsize=14)

# Display the mean and standard deviation on the plot in a box at the bottom left
textstr = f'Mean: {mean_diff:.2f} ms\nSTD: {std_diff:.2f} ms'
props = dict(boxstyle='round', facecolor='white', alpha=0.5)
# plt.text(0.01, 0.02, textstr, transform=plt.gca().transAxes, fontsize=10,
#          verticalalignment='bottom', bbox=props)

plt.text(0.98, 0.97, textstr, transform=plt.gca().transAxes, fontsize=10, ha='right', 
         verticalalignment='top', bbox=props)

# Set the x-axis limits to show the sample range from 0 to the number of differences
plt.xlim(0, len(differences))

plt.ylim(0, 40)

# Show the grid
plt.grid(True)

# Save the plot with a high resolution
plt.savefig('SyncResponseTime.png', dpi=300, bbox_inches='tight')
# plt.savefig('SyncResponseTimeSleep.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()
