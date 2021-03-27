import math
import warnings
from typing import List

import matplotlib.pyplot as plt

import mgrs.sig_mgr as sig_mgr
from domain.sigfeatures import SignalPoint, TimeInterval
from domain.hafeatures import LocLabels


def find_chg_pts(values: List[float]):
    chg_pts: List[int] = []
    prev = values[0]
    for i in range(1, len(values)):
        curr = values[i]
        if curr != prev:
            chg_pts.append(i)
        prev = curr
    return chg_pts


warnings.filterwarnings('ignore')

LOG_PATH = 'resources/uppaal_logs/test2.txt'
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

SIM_ID += 1

plt.figure(figsize=(10, 5))

f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

'''
PARSE TRACES
'''

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hIdle = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.idle')]

'''
IDENTIFY CHANGE POINTS
(FIRST OVERLAY: HUMAN MOVE)
'''

ftg_entries = []
mov_entries = []
idle_entries = []
chg_pts = []
for (i, sim) in enumerate(ftg):
    entries = sim.split('\n')[1:]
    ftg_entries.append(entries)

    entries = hMov[i].split('\n')[1:]
    mov_entries.append(entries)

    entries = hIdle[i].split('\n')[1:]
    idle_entries.append(entries)

    chg_pts.append(find_chg_pts([float(x.split(' ')[1]) for x in mov_entries[i] if len(x.split(' ')) > 1]))

'''
PLOT TRACES WITH OVERLAY
'''

for (i, sim) in enumerate(ftg_entries):
    plt.figure(figsize=(10, 5))
    t = [float(x.split(' ')[0]) for x in sim[1:len(sim) - 1] if len(x.split(' ')) > 1]
    ftg_pts = [float(x.split(' ')[1]) for x in sim[1:len(sim) - 1] if len(x.split(' ')) > 1]
    plt.plot(t, ftg_pts, 'k-', linewidth=1)

    t = [float(x.split(' ')[0]) for x in mov_entries[i][1:len(mov_entries[i]) - 1] if len(x.split(' ')) > 1]
    mov_pts = [float(x.split(' ')[1]) for x in mov_entries[i][1:len(sim) - 1] if len(x.split(' ')) > 1]
    plt.plot(t, mov_pts, 'r--', linewidth=1)

    t = [float(x.split(' ')[0]) for x in idle_entries[i][1:len(idle_entries[i]) - 1] if len(x.split(' ')) > 1]
    idle_pts = [float(x.split(' ')[1]) for x in idle_entries[i][1:len(sim) - 1] if len(x.split(' ')) > 1]
    plt.plot(t, idle_pts, 'g--', linewidth=1)

    [plt.plot(t[n], 1, 'bx', markersize=12) for n in chg_pts[i]]
    plt.show()

'''
SPLIT SEGMENTS AND SET LABEL
'''
segments = []
labels = []
for i in range(len(chg_pts)):
    sim_segm = []
    sim_labels = []
    prev = 0.0
    for pt in chg_pts[i]:
        curr = float(mov_entries[i][pt].split(' ')[0])
        if float(mov_entries[i][pt - 1].split(' ')[1]) == 0.0:
            sim_labels.append(LocLabels.IDLE)
        else:
            sim_labels.append(LocLabels.BUSY)
        sig_pts = list(filter(lambda e: len(e.split(' ')) > 1 and
                                        prev <= float(e.split(' ')[0]) < curr, ftg_entries[i]))
        sig_pts = list(map(lambda x: SignalPoint(float(x.split(' ')[0]), 1, float(x.split(' ')[1])), sig_pts))
        sim_segm.append(sig_pts)
        prev = curr

    if float(mov_entries[i][- 2].split(' ')[1]) == 0.0:
        sim_labels.append(LocLabels.IDLE)
    else:
        sim_labels.append(LocLabels.BUSY)
    curr = float(ftg_entries[i][-2].split(' ')[0])
    sig_pts = list(filter(lambda e: len(e.split(' ')) > 1 and
                                    prev <= float(e.split(' ')[0]) < curr, ftg_entries[i]))
    sig_pts = list(map(lambda x: SignalPoint(float(x.split(' ')[0]), 1, float(x.split(' ')[1])), sig_pts))
    sim_segm.append(sig_pts)

    segments.append(sim_segm)
    labels.append(sim_labels)

'''
ESTIMATE RATES FOR IDENTIFIED SEGMENTS
'''
est_rates = []
for sim in range(len(segments)):
    rates = []
    for segment in segments[sim]:
        t = [pt.timestamp for pt in segment]
        x = [pt.value for pt in segment]
        try:
            dt = TimeInterval(segment[0].timestamp, segment[-1].timestamp)
            params, _, _ = sig_mgr.n_predictions(segment, dt, 10, show_formula=False)
            est_rate = -math.log(params[1]) if params[1] != 0.0 else 0.0
            # print('{} {}'.format(est_rate, labels[sim][segments[sim].index(segment)]))
            rates.append(est_rate)
        except ValueError:
            rates.append(0.0)
            print("Not enough data pts ({})".format(len(segment)))
    est_rates.append(rates)

lambdas = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.BUSY]
mus = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.IDLE]

avg_lambda = sum(lambdas)/len(lambdas)
print(avg_lambda)

avg_mu = sum(mus)/len(mus)
print(avg_mu)
