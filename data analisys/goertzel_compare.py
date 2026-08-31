"""Regenera LatencyCompare.png y LatencyCompareDelay.png.

Correcciones respecto de goertzel_compare.py:
  1. BUG DE ETIQUETADO: el script original calculaba
         dif = (mu + std) - (mu - std)   ->  2*sigma
     y lo imprimia como "+-dif", por lo que las figuras mostraban 9.37 / 10.25 / 10.16 ms
     cuando el desvio estandar real es 4.68 / 5.13 / 5.08 ms.
     Se conserva la notacion "+-" original; lo unico que cambia es el valor (sigma, no 2*sigma).
     N y la definicion de "+-" (media +- un desvio estandar) van en el caption LaTeX,
     no en la leyenda, para no recargarla.
  2. Se elimina np.random.shuffle(lags): el eje "Event Count" ahora es el orden
     cronologico real de los eventos, no una permutacion aleatoria.
  3. Se descartan los fallos de deteccion (lag >= 95% de la ventana de busqueda de
     2000 ms). En esos casos el Goertzel no encontro el tono y el argmax cayo contra
     el borde de la ventana: no son latencias. Se informa cuantos se descartaron.

sigma se calcula con ddof=0 (np.std por defecto), igual que los scripts originales,
para que los valores coincidan con los ya reportados en el texto (4.68 / 5.13 / 5.08).
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = r'C:\Users\gabri\Desktop\pf-anregung\data analisys\studies'
OUT = r'C:\Users\gabri\Workspace\Proyecto-Final---Anregung\02_Images'

FS, F0, N_WIN, TOL = 128, 16, 128, 256
WINDOW_MS = TOL * 1000.0 / FS          # 2000 ms
FAIL_MS = 0.95 * WINDOW_MS             # 1900 ms

WASAPI = os.path.join(BASE, 'wasapi wait', 'study_wait_wasapi_3.csv')
DSOUND = os.path.join(BASE, 'study_wait_dsound_curated.csv')
DELAY = os.path.join(BASE, 'wasapi wait delay 500 ms', 'study_wait_wasapi_500ms_3.csv')


def goertzel_power_sliding(sig):
    """Potencia de Goertzel en f0 para toda ventana deslizante de N_WIN muestras.

    Con f0 = 16 Hz, fs = 128 Hz y N = 128 el bin k = f0*N/fs = 16 es entero, de modo
    que la salida de Goertzel coincide con |DFT[k]|^2 y puede vectorizarse.
    """
    k = F0 * N_WIN // FS
    basis = np.exp(-2j * np.pi * k * np.arange(N_WIN) / N_WIN)
    win = np.lib.stride_tricks.sliding_window_view(sig, N_WIN)
    return np.abs(win @ basis) ** 2


def compute_lags(csv_path):
    data = pd.read_csv(csv_path, header=None,
                       names=['timestamp', 'signal', 'stimuli'], usecols=[0, 1, 2])
    data['ticks'] = range(len(data))
    ts = data['timestamp'].values
    sig = data['signal'].values.astype(float)
    marks = data[pd.notna(data['stimuli']) & (data['stimuli'] != '')]['ticks'].values

    power = goertzel_power_sliding(sig)
    detected, used = [], []
    for m in marks:
        a, b = max(0, m), min(len(sig) - N_WIN, m + TOL)
        if b <= a:
            continue
        vals = power[a:b]
        mask = vals > vals.mean() + vals.std()      # umbral adaptativo mu + 1*sigma
        if mask.any():
            idx = np.arange(a, b)[mask]
            detected.append(idx[np.argmax(vals[mask])])
            used.append(m)

    lags = ts[np.array(detected)] - ts[np.array(used)]
    n_fail = int((lags >= FAIL_MS).sum())
    return lags[lags < FAIL_MS], n_fail


def stats(lags):
    return lags.mean(), lags.std(), len(lags)      # ddof=0, como los scripts originales


def plot_pair(series, title, outfile, ylim, xlim=(0, 100)):
    plt.figure()
    for lags, color, name in series:
        mu, sd, _ = stats(lags)
        plt.plot(np.arange(len(lags)), lags, '-', color=color,
                 label=f'{name} (Mean: {mu:.2f} ms, ±{sd:.2f} ms)')
    plt.title(title, fontsize=16)
    plt.xlabel('Event Count', fontsize=14)
    plt.ylabel('Time Difference (ms)', fontsize=14)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylim(*ylim)
    plt.xlim(*xlim)
    plt.savefig(os.path.join(OUT, outfile), dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  -> {outfile}')


lags_w, fail_w = compute_lags(WASAPI)
lags_d, fail_d = compute_lags(DSOUND)
lags_delay, fail_delay = compute_lags(DELAY)

for name, lags, fail in [('WASAPI', lags_w, fail_w),
                         ('DirectSound', lags_d, fail_d),
                         ('WASAPI +500ms', lags_delay, fail_delay)]:
    mu, sd, n = stats(lags)
    print(f'{name:16s} N={n:4d}  mean={mu:7.2f} ms  SD={sd:5.2f} ms  '
          f'(fallos de deteccion descartados: {fail})')

print('\nFiguras regeneradas:')
plot_pair([(lags_w, 'skyblue', 'WASAPI'), (lags_d, 'green', 'DirectSound')],
          'Sound Library Comparison', 'LatencyCompare.png', ylim=(90, 200))
plot_pair([(lags_w, 'skyblue', 'WASAPI'), (lags_delay, 'orange', 'WASAPI with 500ms delay')],
          'Delay Comparison', 'LatencyCompareDelay.png', ylim=(90, 800))
