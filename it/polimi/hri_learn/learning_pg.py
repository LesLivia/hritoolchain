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

import mgrs.sig_mgr as sig_mgr
import pltr.ha_pltr as ha_pltr
import pltr.sig_pltr as sig_pltr
from domain.hafeatures import HybridAutomaton, LOCATIONS, Edge
from domain.sigfeatures import SignalPoint, ChangePoint, SignalType, Labels, TimeInterval

warnings.filterwarnings('ignore')

LOG_PATH = "resources/sim_logs/sim{}"
FTG_LOG = 'humanFatigue.log'
POS_LOG = 'humanPosition.log'
CHG_LOG = 'robotBattery.log'
ROB_POS_LOG = 'robotPosition.log'
HUM_ID = 1
ROB_ID = 1

SIM_ID = 1

REAL_PROFILES = [(0.0005, 0.0005), (0.01, 0.004), (0.008, 0.0035)]
LAMBDA_EST: float
MU_EST: float


def read_file(path: str, is_hum=True):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    lines = list(filter(lambda l: len(l) > 2, lines))
    if is_hum:
        lines = list(filter(lambda l: l.split(':')[1] == 'hum' + str(HUM_ID), lines))
    return lines


while os.path.isdir(LOG_PATH.format(SIM_ID)) and False:
    print('-> SIM {}'.format(SIM_ID))
    estimated_lambdas = []
    estimated_mus = []

    ftg_lines = read_file(LOG_PATH.format(SIM_ID) + '/' + FTG_LOG)
    ftg_sig: List[SignalPoint] = sig_mgr.read_signal(ftg_lines, SignalType.NUMERIC)

    change_pts: List[ChangePoint] = sig_mgr.identify_change_pts(ftg_sig)
    # PREDICT FUTURE VALUES
    for (index, pt) in enumerate(change_pts):
        if index != 0:
            dt: TimeInterval = TimeInterval(change_pts[index - 1].dt.t_max, pt.dt.t_min)
            try:
                param_est, x_fore, forecasts = sig_mgr.n_predictions(ftg_sig, dt, 50)
                if pt.event == Labels.STOPPED:
                    estimated_lambdas.append(param_est)
                else:
                    estimated_mus.append(param_est)
            except (ValueError, ZeroDivisionError):
                pass

    print(estimated_lambdas)
    try:
        LAMBDA_EST = sum(estimated_lambdas) / len(estimated_lambdas)
        errors = []
        for (lambda_real, mu_real) in REAL_PROFILES:
            mean_error = sum(list(map(lambda i: abs(i - lambda_real) / lambda_real * 100, estimated_lambdas))) / len(
                estimated_lambdas)
            errors.append(mean_error)

        print('Mean Estimated LAMBDA: {:.6f}'.format(LAMBDA_EST))
        print('Minimum LAMBDA Estimation Error: {:.6f}%'.format(min(errors)))
    except ZeroDivisionError:
        print('No value of LAMBDA could be estimated')

    print(estimated_mus)
    try:
        MU_EST = sum(estimated_mus) / len(estimated_mus)
        errors = []
        for (lambda_real, mu_real) in REAL_PROFILES:
            mean_error = sum(list(map(lambda i: abs(i - mu_real) / mu_real * 100, estimated_mus))) / len(estimated_mus)
            errors.append(mean_error)

        print('Mean Estimated MU: {:.6f}'.format(MU_EST))
        print('Minimum MU Estimation Error: {:.6f}%'.format(min(errors)))
    except ZeroDivisionError:
        print('No value of MU could be estimated')

    # HA with t-guards
    LOCATIONS[0].set_flow_cond('F\' == -Fp*{:.4f}*exp(-{:.4f}*t)'.format(MU_EST, MU_EST))
    LOCATIONS[1].set_flow_cond('F\' == Fp*{:.4f}*exp(-{:.4f}*t)'.format(LAMBDA_EST, LAMBDA_EST))
    HUM_HA: HybridAutomaton = HybridAutomaton(LOCATIONS, [])
    edges: List[Edge] = [Edge(LOCATIONS[0], LOCATIONS[1], 'START?'), Edge(LOCATIONS[1], LOCATIONS[0], 'STOP?')]
    HUM_HA.set_edges(edges)
    ha_pltr.plot_ha(HUM_HA, 'HUM_HA', view=False)

    sig_pltr.plot_sig(ftg_sig, change_pts, with_pred=False)

    pos_lines = read_file(LOG_PATH.format(SIM_ID) + '/' + POS_LOG)
    pos_sig: List[SignalPoint] = sig_mgr.read_signal(pos_lines, SignalType.POSITION)

    rob_pos_lines = read_file(LOG_PATH.format(SIM_ID) + '/' + ROB_POS_LOG, is_hum=False)
    rob_pos_sig: List[SignalPoint] = sig_mgr.read_signal(rob_pos_lines, SignalType.POSITION, diff_id=False)

    dist_sig: List[SignalPoint] = []
    for pt in pos_sig:
        rob_pos = list(filter(lambda r_pt: r_pt.timestamp == pt.timestamp, rob_pos_sig))
        if len(rob_pos) > 0:
            dist_sig.append(SignalPoint(pt.timestamp, HUM_ID, sig_mgr.pt_dist(pt.value, rob_pos[0].value)))
    # sig_mgr.print_signal(dist_sig)
    # sig_pltr.plot_sig(dist_sig, change_pts)

    SIM_ID += 1

# PLAYGROUND with ECG signal
print('-----------------------------')


def line_to_emg(line: str):
    sampling_rate = 700
    fields = line.split('	')
    timestamp = float(fields[0], ) * 1 / sampling_rate
    # ((signal/chan_bit-0.5)*vcc)
    emg = (float(fields[4]) / 2 ** 16 - 0.5) * 3
    return SignalPoint(timestamp, 1, emg)


data, header = bsnb.load_signal('emg_fatigue', get_header=True)
mac = "00:07:80:79:6F:DB"  # Mac-address
channel = "CH" + str(header["channels"][0])
sr = header["sampling rate"]
resolution = 16  # Resolution (number of available bits)
signal_mv = data[channel]
vcc = 3000  # mV
gain = 1000
time = bsnb.generate_time(signal_mv, sr)

plt.figure(figsize=(30, 5))
plt.plot(time, signal_mv)

emg_data = []
for (index, val) in enumerate(signal_mv):
    emg_data.append(SignalPoint(time[index], 1, val))

activation_begin, activation_end = bsnb.detect_emg_activations([point.value for point in emg_data], sr)[
                                   :2]
median_freq_data = []
mean_freq_data = []
for (index, start) in enumerate(activation_begin):
    emg_pts = emg_data[start: activation_end[index]]
    freqs, power = periodogram([point.value for point in emg_pts], fs=sr)
    area_freq = cumtrapz(power, freqs, initial=0)
    total_power = area_freq[-1]
    # MDF
    median_freq_data += [freqs[where(area_freq >= total_power / 2)[0][0]]]
    # MNF
    mnf = sum(freqs * power) / sum(power)
    mean_freq_data.append(math.log(mnf))

bursts = [x / sr for x in activation_end]
print(bursts)
print(mean_freq_data)

model = LinearRegression()
model.fit(np.array(bursts).reshape((-1, 1)), mean_freq_data)
q = model.intercept_
m = model.coef_
print('ESTIMATED RATE: {}'.format(m))
x = np.arange(0, 1700, 0.1)
est_values = [q + m * t for t in x]

plt.figure()
plt.plot(bursts, mean_freq_data, 'b', x, est_values, 'r')
plt.show()

plt.figure()
x = np.arange(0, 2000, 1)
exp_ftg = [1 - math.exp(-math.fabs(m) * t) for t in x]
MET = len(list(filter(lambda p: p < 0.98, exp_ftg)))
print('MET: {}, ln(MNF[MET]): {}'.format(MET, q + m * MET))

plt.plot(x[:MET], [1 - math.exp(-math.fabs(m) * t) for t in x[:MET]])
plt.show()
