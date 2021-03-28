import math
import warnings
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
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

'''
PARSE TRACES
'''
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

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
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    ftg_entries.append(entries)

    entries = hMov[i].split('\n')[1:]
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    mov_entries.append(entries)

    entries = hIdle[i].split('\n')[1:]
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
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
        dts = [v - t[i - 1] for i, v in enumerate(t) if i > 0]
        avg_dt = sum(dts) / len(dts)
        x = [pt.value for pt in segment]
        try:
            dt = TimeInterval(segment[0].timestamp, segment[-1].timestamp)
            params, x_fore, fore = sig_mgr.n_predictions(segment, dt, 10, show_formula=False)
            est_rate = -math.log(params[1]) / avg_dt * 2 if params[1] != 0.0 else 0.0
            print('{:.5f} {}'.format(est_rate, labels[sim][segments[sim].index(segment)]))
            rates.append(est_rate)
        except ValueError:
            rates.append(None)
            print("Not enough data pts ({})".format(len(segment)))
    est_rates.append(rates)

'''
HYPOTHESIS TESTING on ESTIMATED RATES
'''
IDLE_DISTR = (0.005, 0.00008)
BUSY_DISTR = (0.002, 0.00008)

x = np.linspace(IDLE_DISTR[0] - 3 * IDLE_DISTR[1], IDLE_DISTR[0] + 3 * IDLE_DISTR[1], 100)
idle_norm = stats.norm.pdf(x, IDLE_DISTR[0], IDLE_DISTR[1])
mus = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.IDLE]

plt.figure()
plt.plot(x, idle_norm, 'b', mus, [0]*len(mus), 'rx')
plt.show()

x = np.linspace(BUSY_DISTR[0] - 3 * BUSY_DISTR[1], BUSY_DISTR[0] + 3 * BUSY_DISTR[1], 100)
busy_norm = stats.norm.pdf(x, BUSY_DISTR[0], BUSY_DISTR[1])
lambdas = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.BUSY]

plt.figure()
plt.plot(x, busy_norm, 'b', lambdas, [0]*len(lambdas), 'rx')
plt.show()
