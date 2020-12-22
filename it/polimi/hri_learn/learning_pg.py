import math
import os
import warnings
from typing import List

import mgrs.hrv_mgr as hrv_mgr
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


while os.path.isdir(LOG_PATH.format(SIM_ID)) and True:
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
# index = 0
# ecg_sig: List[SignalPoint] = []
# while os.path.isfile('resources/hrv_pg/100m ({}).mat'.format(index)):
#     mat = sio.loadmat('resources/hrv_pg/100m ({}).mat'.format(index))
#     start_i = len(ecg_sig)
#     ecg_data = mat['val'][0]
#     ecg_data = [SignalPoint((i + start_i) / 360, 1, value / 200) for (i, value) in enumerate(ecg_data)]
#     ecg_sig += ecg_data
#     index += 1
# print(len(ecg_sig))
# sdnns: List[SignalPoint] = []
# for i in range(0, len(ecg_sig) - 3600, 3600):
#     segment = ecg_sig[i:i + 3600]
#     peaks, res = hrv_mgr.get_hrv_data(segment)
#     sdnns.append(SignalPoint((i + 3600)/3600, 1, res['hr_mean']))
# sig_pltr.plot_sig(ecg_sig, [])
# sig_pltr.plot_sig(sdnns, [])

with open('resources/hrv_pg/S2_respiban.txt') as f:
    all_lines = f.readlines()
    all_lines = list(filter(lambda l: not l.startswith('#'), all_lines))
    sdnns = []
    sampling_rate = 700
    window = 60 * sampling_rate
    end = math.ceil(len(all_lines) / 2) - window
    for i in range(0, end, window):
        lines = all_lines[i:window + i]
        ecg_pts = list(
            map(lambda l: SignalPoint(float(l.split('	')[0], ) * 1 / sampling_rate, 1, float(l.split('	')[2])),
                lines))
        # sig_pltr.plot_sig(ecg_pts, [])
        peaks, res = hrv_mgr.get_hrv_data(ecg_pts, show=False)
        sdnns.append(SignalPoint(i, 1, res['sdnn']))
        print('{:.1f}% completed'.format(i / end * 100))
    chg_pts = [ChangePoint(TimeInterval(0, 297360), Labels.STOPPED),
               ChangePoint(TimeInterval(1105440, 1661100), Labels.STARTED)]
    sig_pltr.plot_sig(sdnns, chg_pts, with_pred=True, n_pred=10)
