import os
import warnings
from typing import List

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

LAMBDA_REAL = 0.0005
MU_REAL = 0.0005
LAMBA_EST: float
MU_EST: float


def read_file(path: str, is_hum=True):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    lines = list(filter(lambda l: len(l) > 2, lines))
    if is_hum:
        lines = list(filter(lambda l: l.split(':')[1] == 'hum' + str(HUM_ID), lines))
    return lines


estimated_lambdas = []
estimated_mus = []
while os.path.isdir(LOG_PATH.format(SIM_ID)):
    print('-> SIM {}'.format(SIM_ID))
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

    sig_pltr.plot_sig(ftg_sig, change_pts, with_pred=True)

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

print(estimated_lambdas)
try:
    LAMBDA_EST = sum(estimated_lambdas) / len(estimated_lambdas)
    mean_error = sum(list(map(lambda i: (i - LAMBDA_REAL) / LAMBDA_REAL * 100, estimated_lambdas))) / len(
        estimated_lambdas)

    print('Mean Estimation Error for LAMBDA: {:.4f}%'.format(mean_error))
except ZeroDivisionError:
    print('No value of LAMBDA could be estimated')

print(estimated_mus)
try:
    MU_EST = sum(estimated_mus) / len(estimated_mus)
    mean_error = sum(list(map(lambda i: (i - MU_REAL) / MU_REAL * 100, estimated_lambdas))) / len(
        estimated_mus)
    print('Mean Estimation Error for MU: {:.4f}%'.format(mean_error))
except ZeroDivisionError:
    print('No value of MU could be estimated')

# HA with t-guards
LOCATIONS[0].set_flow_cond('F\' == -Fp*{:.4f}*exp(-{:.4f}*t)'.format(MU_EST, MU_EST))
LOCATIONS[1].set_flow_cond('F\' == Fp*{:.4f}*exp(-{:.4f}*t)'.format(LAMBDA_EST, LAMBDA_EST))
HUM_HA: HybridAutomaton = HybridAutomaton(LOCATIONS, [])
edges: List[Edge] = [Edge(LOCATIONS[0], LOCATIONS[1], 'START?'), Edge(LOCATIONS[1], LOCATIONS[0], 'STOP?')]
HUM_HA.set_edges(edges)
ha_pltr.plot_ha(HUM_HA, 'HUM_HA', view=True)
