import numpy as np
from scipy.io.wavfile import write

# Parameters
rate = 44100    # samples per second
T = 1           # sample duration (seconds)
f = 16         # frequency (Hz) of the sine wave

# Compute waveform samples
t = np.linspace(0, T, T*rate, endpoint=False)
x = 0.5 * np.sin(2*np.pi * f * t)

# Convert samples to 16-bit 2's complement values
samples = np.int16(x * 32767)

# Write the .wav file
write('16HzB.wav', rate, np.array([samples, samples]).T)
