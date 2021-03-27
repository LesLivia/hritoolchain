import warnings
from typing import List
import mgrs.sig_mgr

import matplotlib.pyplot as plt


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

    [plt.plot(t[n], mov_pts[n], 'bx', markersize=12) for n in chg_pts[i]]
    plt.show()

'''
ESTIMATE RATES FOR IDENTIFIED SEGMENTS
'''
