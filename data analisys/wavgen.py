import numpy as np
from scipy.io import wavfile

# Set the parameters
duration = 1  # in seconds
frequency = 10000  # in Hz
sampling_rate = 44100  # in Hz

# Generate the sine wave
time = np.arange(0, duration, 1/sampling_rate)
amplitude = np.sin(2 * np.pi * frequency * time)

# Scale the amplitude to fit the range [-32768, 32767]
scaled_amplitude = np.int16(amplitude * 32767)

# Save the audio as a .wav file
wavfile.write('10000hz.wav', sampling_rate, scaled_amplitude)