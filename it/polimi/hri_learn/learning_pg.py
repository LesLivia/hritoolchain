import math
import os
import warnings
from typing import List

import biosignalsnotebooks as bsnb
import numpy as np
import scipy.io

import mgrs.emg_mgr as emg_mgr
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
                    estimated_lambdas.append(-math.log(param_est[1]))
                else:
                    estimated_mus.append(-math.log(param_est[1]))
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

# data, header = bsnb.load_signal('emg_fatigue', get_header=True)
# mac = "00:07:80:79:6F:DB"  # Mac-address
# channel = "CH" + str(header["channels"][0])
# sr = header["sampling rate"]
# resolution = 16  # Resolution (number of available bits)
# signal_mv = data[channel]
# vcc = 3000  # mV
# gain = 1000
# time = bsnb.generate_time(signal_mv, sr)

INDEX = 5
category = 'y'

while os.path.isdir('resources/hrv_pg/{}{}'.format(category, INDEX)):
    df = scipy.io.loadmat('resources/hrv_pg/{}{}/rawdata.mat'.format(category, INDEX))
    mask = scipy.io.loadmat('resources/hrv_pg/{}{}/spikeindicator.mat'.format(category, INDEX))
    to_use = mask['trial1sd'][:, 3].astype(np.bool)
    sr = 1080
    signal_mv = df['trial1'][~to_use, 3]
    lim = int(2.5 * 60 * sr)
    signal_mv = signal_mv[:lim]
    time = bsnb.generate_time(signal_mv, sr)

    # plt.figure(figsize=(30, 5))
    # plt.plot(time, signal_mv)
    # plt.show()
    try:
        mean_freq_data = emg_mgr.calculate_mnf(signal_mv, sr)

        b_s, b_e = emg_mgr.get_bursts(signal_mv, sr)
        bursts = b_e / sr
        q, m, x, est_values = emg_mgr.mnf_lin_reg(mean_freq_data, bursts)

        # plt.figure()
        # plt.plot(bursts, mean_freq_data, 'b', x, est_values, 'r')
        # plt.show()
    except ValueError:
        print('unexpected behavior')

    if (category == 'y' and INDEX < 21) or (category == 'e'):
        INDEX += 1
    else:
        print('switching to elders')
        category = 'e'
        INDEX = 7

# plt.figure()
# x = np.arange(0, 2000, 1)
# exp_ftg = [1 - math.exp(-math.fabs(m) * t) for t in x]
# MET = len(list(filter(lambda p: p < 0.98, exp_ftg)))
# print('MET: {}, ln(MNF[MET]): {}'.format(MET, q + m * MET))
#
# plt.plot(x[:MET], [1 - math.exp(-math.fabs(m) * t) for t in x[:MET]])
# plt.show()
#
# params, x_fore, forecasts = sig_mgr.n_predictions(
#     [SignalPoint(index, 1, i) for (index, i) in enumerate(exp_ftg[:120])],
#     TimeInterval(0, 120), 10,
#     show_formula=True)
# print(-math.log(params[1]))

# def line_to_time(line: str, sr: int):
#     raw = line.split('	')[0]
#     # ((signal/chan_bit-0.5)*vcc)
#     t = float(raw) * 1 / sr
#     return t
#
#
# def line_to_emg(line: str):
#     raw = line.split('	')[4]
#     # ((signal/chan_bit-0.5)*vcc)
#     emg = (float(raw) / 2 ** 16 - 0.5) * 3
#     return emg

# with open('resources/hrv_pg/S3_respiban.txt') as wesad_df:
#     lines = wesad_df.readlines()
#     lines = lines[3:]
#     sr = 700
#     x = [line_to_time(line, sr) for line in lines]
#     y = [line_to_emg(line) for line in lines]
#     lim = 5 * 60 * sr
#     plt.figure(figsize=(40, 10))
#     plt.plot(x[:lim], y[:lim])
#     plt.show()
#
#     b_s, b_e = bsnb.detect_emg_activations(y[:lim], sr)[:2]
#     mean_freq_data = []
#     for (index, start) in enumerate(b_s):
#         emg_pts = y[start: b_e[index]]
#         freqs, power = periodogram(emg_pts, fs=sr)
#         # MNF
#         mnf = sum(freqs * power) / sum(power)
#         mean_freq_data.append(math.log(mnf))
#
#     model = LinearRegression()
#     model.fit(np.array(b_e / sr).reshape((-1, 1)), mean_freq_data)
#     q = model.intercept_
#     m = model.coef_
#     x = np.arange(0, lim / sr, 1)
#     est_values = [q + m * t for t in x]
#     plt.figure()
#     plt.plot(b_e / sr, mean_freq_data, 'b', x, est_values, 'r')
#     plt.show()
