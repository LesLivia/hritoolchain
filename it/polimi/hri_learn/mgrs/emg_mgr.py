import math
from typing import List

import biosignalsnotebooks as bsnb
import numpy as np
from scipy import signal
from scipy.signal import periodogram
from sklearn.linear_model import LinearRegression


def get_bursts(emg_data: List[float], sr: int):
    return bsnb.detect_emg_activations(emg_data, sr)[:2]


def calculate_mnf(emg_data: List[float], sr: int):
    b_s, b_e = get_bursts(emg_data, sr)
    mean_freq_data = []
    for (index, start) in enumerate(b_s):
        emg_pts = emg_data[start: b_e[index]]
        freqs, power = periodogram(emg_pts, fs=sr)
        # MNF
        mnf = sum(freqs * power) / sum(power)
        mean_freq_data.append(math.log(mnf))

    # First, design the Buterworth filter
    N = 3  # Filter order
    Wn = 0.3  # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    cf = 0.0001
    smooth_data = signal.filtfilt(B, A, mean_freq_data)
    smooth_data = [i * (1 - cf * index) for (index, i) in enumerate(smooth_data)]
    # plt.plot(mean_freq_data, 'r-')
    # plt.plot(smooth_data, 'b-')
    # plt.show()

    return smooth_data


def mnf_lin_reg(mean_freq_data: List[float], bursts: List[float]):
    model = LinearRegression()
    model.fit(np.array(bursts).reshape((-1, 1)), mean_freq_data)
    q = model.intercept_
    m = model.coef_
    if m > 0:
        raise ValueError
    x = np.arange(0, max(bursts), 0.1)
    est_values = [q + m * t for t in x]
    return q, m, x, est_values
