"""Genera CouplingExample.png y CouplingAmplitude.png.

CouplingExample.png  : traza cruda de AF3 alrededor de un evento representativo,
                       mostrando el parpadeo, el artefacto de 16 Hz del feedback y
                       los dos instantes que definen la latencia end-to-end.
CouplingAmplitude.png: amplitud del componente de 16 Hz en baseline vs feedback
                       para todos los eventos de la sesion.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view

BASE = r'C:\Users\gabri\Desktop\pf-anregung\data analisys\studies'
OUT = r'C:\Users\gabri\Workspace\Proyecto-Final---Anregung\02_Images'
# La traza de ejemplo sale de la unica sesion WASAPI+pacing cuyas marcas coinciden
# con un parpadeo real (deflexion de ~143 uV pico a pico en la marca, frente a ~18 uV
# en las demas). Las sesiones 'wasapi wait/study_wait_wasapi_*.csv' tienen marcas
# generadas por temporizador y no contienen parpadeos que mostrar.
PATH = os.path.join(BASE, 'study_wait_stamp_wasapi_gs_1.csv')
# La estadistica poblacional usa la sesion larga: lo que cuantifica es el acoplamiento
# del feedback en el canal, que no depende de que disparo el evento.
PATH_POP = os.path.join(BASE, 'wasapi wait', 'study_wait_wasapi_3.csv')

FS, F0, N, TOL = 128, 16, 128, 256
K = F0 * N // FS
BASIS = np.exp(-2j * np.pi * K * np.arange(N) / N)
# uV por count del ADC. El equipo usado es el EPOC version 1 (2012), para el que
# Ramele et al. 2022 (arXiv:2206.09051, Tabla 1) reportan 1 LSB = 1.95 uV.
# El valor de 0.51 uV/LSB que publica Emotiv corresponde al EPOC+ (2014), un modelo
# posterior. Las conclusiones sobre acoplamiento dependen solo del cociente
# feedback/baseline y de la separacion de las distribuciones, ambos adimensionales.
UV = 1.95


def load(path):
    ts, sig, stim = [], [], []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = [x.strip() for x in line.strip().split(',')]
            if len(p) < 2:
                continue
            try:
                t, s = float(p[0]), float(p[1])
            except ValueError:
                continue
            ts.append(t); sig.append(s); stim.append(p[2] if len(p) > 2 and p[2] else None)
    return np.array(ts), np.array(sig, float), stim


ts, sig, stim = load(PATH)
marks = np.array([i for i, s in enumerate(stim) if s is not None])
power = np.abs(sliding_window_view(sig, N) @ BASIS) ** 2

# Para la traza de amplitud del panel inferior se usa una ventana corta y CENTRADA.
# La ventana de 1 s del detector, indexada por su muestra inicial, produce una rampa
# triangular de +-1 s alrededor del onset que sugeriria falsamente que el 16 Hz ya
# esta presente antes del parpadeo. Con 32 muestras (250 ms, 4 ciclos completos de
# 16 Hz, bin k = 4 entero) la transicion en el onset queda nitida.
NV = 32
BASIS_V = np.exp(-2j * np.pi * (F0 * NV // FS) * np.arange(NV) / NV)
_amp_raw = 2.0 * np.abs(sliding_window_view(sig - sig.mean(), NV) @ BASIS_V) / NV * UV
amp = np.full(len(sig), np.nan)
amp[NV // 2: NV // 2 + len(_amp_raw)] = _amp_raw      # centrada en la ventana


def onset_for(m):
    a, b = max(0, m), min(len(sig) - N, m + TOL)
    v = power[a:b]
    mk = v > v.mean() + v.std()
    if not mk.any():
        return None
    return int(np.arange(a, b)[mk][np.argmax(v[mk])])


# --- elegir un evento REPRESENTATIVO: el de amplitud de 16 Hz mas cercana a la mediana ---
# (elegir el blink de mayor amplitud daria un ejemplo optimista y no representativo)
cands = []
for m_ in marks:
    o = onset_for(m_)
    if o is None or m_ - 2 * N < 0 or o + 3 * N > len(sig):
        continue
    seg = sig[o:o + N]
    cands.append((m_, o, 2 * np.abs((seg - seg.mean()) @ BASIS) / N * UV))
med = np.median([c[2] for c in cands])
m, onset, ex_amp = min(cands, key=lambda c: abs(c[2] - med))
lat = ts[onset] - ts[m]

# ================= Figura 1: traza cruda =================
lo, hi = m - int(0.6 * FS), onset + 2 * N
t = (ts[lo:hi] - ts[m]) / 1000.0
trace = (sig[lo:hi] - np.median(sig[m - N:m])) * UV

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                               gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(t, trace, color='0.25', linewidth=0.9)
ax1.axvline(0, color='tab:red', linewidth=1.6, label='Blink detected (online threshold)')
ax1.axvline((ts[onset] - ts[m]) / 1000.0, color='tab:blue', linewidth=1.6,
            linestyle='--', label=f'Feedback onset (Goertzel), {lat:.0f} ms later')
ax1.axvspan((ts[onset] - ts[m]) / 1000.0,
            (ts[min(onset + N, len(ts) - 1)] - ts[m]) / 1000.0,
            color='tab:blue', alpha=0.10, label='16 Hz feedback burst (1 s)')
ax1.set_ylabel('AF3 (µV)')
ax1.set_title('Blink-triggered feedback captured on the same EEG channel')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, alpha=0.3)

ax2.plot(t, amp[lo:hi], color='tab:blue', linewidth=1.2)
ax2.axvline(0, color='tab:red', linewidth=1.6)
ax2.axvline((ts[onset] - ts[m]) / 1000.0, color='tab:blue', linewidth=1.6, linestyle='--')
ax2.set_ylabel('16 Hz amplitude (µV)')
ax2.set_xlabel('Time relative to blink detection (s)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT, 'CouplingExample.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f'  -> CouplingExample.png  (evento muestra {m}, latencia {lat:.0f} ms, amp16 {ex_amp:.1f} uV = mediana)')

# ================= Figura 2: baseline vs feedback =================
ts, sig, stim = load(PATH_POP)
marks = np.array([i for i, s in enumerate(stim) if s is not None])
power = np.abs(sliding_window_view(sig, N) @ BASIS) ** 2

# El segundo previo a la marca no sirve como baseline: la rafaga del evento anterior
# termina unos 850 ms antes y su cola contamina la estimacion (17.2 uV en vez de 2.0).
# Se usa la ventana de 750 a 250 ms antes de la marca, ya libre de feedback.
NB = 64
BASIS_B = np.exp(-2j * np.pi * (F0 * NB // FS) * np.arange(NB) / NB)
base_a, fb_a = [], []
for mk_ in marks:
    o = onset_for(mk_)
    if o is None or mk_ - 96 < 0 or o + N > len(sig):
        continue
    b = sig[mk_ - 96:mk_ - 32]; f = sig[o:o + N]
    base_a.append(2 * np.abs((b - b.mean()) @ BASIS_B) / NB * UV)
    fb_a.append(2 * np.abs((f - f.mean()) @ BASIS) / N * UV)
base_a, fb_a = np.array(base_a), np.array(fb_a)

fig, ax = plt.subplots(figsize=(7, 4.2))
bins = np.linspace(0, max(fb_a.max(), base_a.max()) * 1.05, 40)
ax.hist(base_a, bins=bins, alpha=0.65, color='tab:gray',
        label=f'Baseline, 750-250 ms before the marker (mean {base_a.mean():.1f} µV)')
ax.hist(fb_a, bins=bins, alpha=0.65, color='tab:blue',
        label=f'During feedback (mean {fb_a.mean():.1f} µV)')
ax.axvline(base_a.max(), color='tab:red', linestyle=':', linewidth=1.5,
           label=f'Max baseline ({base_a.max():.1f} µV)')
ax.set_xlabel('Amplitude of the 16 Hz component on AF3 (µV)')
ax.set_ylabel('Number of events')
ax.set_title(f'Coupling of the electrical feedback into the EEG channel (N = {len(fb_a)})')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'CouplingAmplitude.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f'  -> CouplingAmplitude.png  (baseline {base_a.mean():.2f} uV, feedback {fb_a.mean():.2f} uV, '
      f'separacion {100*(fb_a > base_a.max()).mean():.0f}%)')
