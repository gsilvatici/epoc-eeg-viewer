import pandas as pd
import matplotlib.pyplot as plt

file_path = 'C:\\Users\\gabri\\Desktop\\BCI\\epoceeg-master\\study_nowait_device_latency_3.csv'

# Read timestamps from the CSV file
df = pd.read_csv(file_path, header=None, usecols=[0], names=['timestamp'])

# Clean the data by removing rows with non-numeric values
df = df[pd.to_numeric(df['timestamp'], errors='coerce').notnull()]
df['timestamp'] = pd.to_numeric(df['timestamp'])

# Select the last 300 samples and reset index
df = df.tail(300).reset_index(drop=True)

# Calculate time differences in milliseconds
df['difference'] = df['timestamp'].diff()

# Remove the first NaN value after diff()
df = df.dropna().reset_index(drop=True)

# Calculate the mean and standard deviation of the differences
mean_diff = df['difference'].mean()
std_diff = df['difference'].std()

# Plot the data without error bars, using a lighter shade of blue
plt.plot(df.index, df['difference'], '-o', color='skyblue')

# Set the plot title and labels
plt.title('Sample-to-Sample Time', fontsize=16)
plt.xlabel('Sample', fontsize=14)
plt.ylabel('Time Difference (ms)', fontsize=14)

# Display the mean and standard deviation on the plot in a box at the bottom left
textstr = f'Mean: {mean_diff:.2f} ms\nSTD: {std_diff:.2f} ms'
props = dict(boxstyle='round', facecolor='white', alpha=0.5)
plt.text(0.05, 0.05, textstr, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='bottom', bbox=props)

# Set the x-axis limits to show the sample range from 0 to 300
plt.xlim(0, 300)

# Show the grid
plt.grid(True)

# Save the plot with a high resolution
plt.savefig('SampleToSample.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()
