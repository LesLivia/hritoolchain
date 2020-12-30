import math
import os
import warnings
from typing import List

import biosignalsnotebooks as bsnb
import matplotlib.pyplot as plt
import numpy as np
from numpy import where
from scipy.integrate import cumtrapz
from scipy.signal import periodogram
from sklearn.linear_model import LinearRegression
import scipy.io
import mgrs.sig_mgr as sig_mgr
import pltr.ha_pltr as ha_pltr
import pltr.sig_pltr as sig_pltr
from domain.hafeatures import HybridAutomaton, LOCATIONS, Edge
from domain.sigfeatures import SignalPoint, ChangePoint, SignalType, Labels, TimeInterval


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
    return mean_freq_data


def mnf_lin_reg(mean_freq_data: List[float], bursts: List[float]):
    model = LinearRegression()
    model.fit(np.array(bursts).reshape((-1, 1)), mean_freq_data)
    q = model.intercept_
    m = model.coef_
    if m > 0:
        raise ValueError
    print('ESTIMATED RATE: {:.6f}'.format(math.fabs(m)))
    x = np.arange(0, max(bursts), 0.1)
    est_values = [q + m * t for t in x]
    return q, m, x, est_values
