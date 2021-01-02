import math
import os
import random
import warnings
from typing import List

import biosignalsnotebooks as bsnb
import matplotlib.pyplot as plt
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
muscle = 3
count = 0
MAX = 35

est_lambdas = []
METs = []
while os.path.isdir('resources/hrv_pg/{}{}'.format(category, INDEX)) and count < MAX:
    trial = random.randint(1, 10)
    print('SUBJECT {}{}, trial {}'.format(category, INDEX, trial))
    df = scipy.io.loadmat('resources/hrv_pg/{}{}/rawdata.mat'.format(category, INDEX))
    mask = scipy.io.loadmat('resources/hrv_pg/{}{}/spikeindicator.mat'.format(category, INDEX))
    try:
        to_use = mask['trial{}sd'.format(trial)][:, muscle].astype(np.bool)
    except IndexError:
        muscle = 0
        to_use = mask['trial{}sd'.format(trial)][:, muscle].astype(np.bool)
    sr = 1080
    signal_mv = df['trial{}'.format(trial)][~to_use, muscle]
    lim = int(5 * 60 * sr)
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

        est_lambda = math.fabs(m)
        MET = math.log(1 - 0.95) / -est_lambda / 60
        est_lambdas.append(math.fabs(m))
        METs.append(MET)
        print('ESTIMATED RATE: {:.6f}, MET: {:.2f}min'.format(est_lambda, MET))

        plt.figure()
        plt.plot(bursts, mean_freq_data, 'b', x, est_values, 'r')
        plt.show()
    except ValueError:
        print('invalid data')

    if (category == 'y' and INDEX < 21) or (category == 'e'):
        INDEX += 1
    else:
        print('switching to elders')
        category = 'e'
        INDEX = 7
    count = count + 1

plt.figure()
plt.plot(METs)
plt.show()
