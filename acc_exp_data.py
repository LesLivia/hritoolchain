import os
import matplotlib.pyplot as plt
from typing import List


def parse_file(path: str):
    f = open(path)
    lines = f.readlines()
    # 1.00: hum1:0.00099700449550337
    # 1.00: 29.9286
    t = [float(line.split(':')[0]) for line in lines if line != '\n']
    vals = [float(line.split(':')[-1]) for line in lines if line != '\n']
    return t, vals


def find_last_chg_pt(t: List[float], v: List[float]):
    for i in range(len(v) - 1, 1, -1):
        if v[i] > v[i - 1]:
            return t[i - 1]
    else:
        return 0.0


LOG_DIR = "/Users/lestingi/Desktop/logs/sim_logs/exp1a"
SIM_LOGS_DIRS = [x[0] for x in os.walk(LOG_DIR)]
SIM_LOGS_DIRS = list(filter(lambda x: x.startswith(LOG_DIR + '/SIM_2021-07'), SIM_LOGS_DIRS))

FTG_FILE = '/humanFatigue.log'
CHG_FILE = '/robotBattery.log'
OUT_FILE = '/outfile.txt'

print('FOUND {} SIMULATION TO ANALYZE'.format(len(SIM_LOGS_DIRS)))

# PLOT FTG CURVES

ftg_t, ftg_pts = zip(*[parse_file(s + FTG_FILE) for s in SIM_LOGS_DIRS])

plt.figure(figsize=(10, 5))
plt.xlabel('t[s]', fontsize=18)
plt.ylabel('F[0-1]', fontsize=18)

for (i, t) in enumerate(ftg_t):
    if i == 0:
        plt.plot(t, ftg_pts[i], '--', color='black', linewidth=0.25, alpha=0.5,
                 label='simulations ({})'.format(len(SIM_LOGS_DIRS)))
    else:
        plt.plot(t, ftg_pts[i], '--', color='black', linewidth=0.25, alpha=0.5)

avg_t = [t for t in ftg_t if len(t) == max([len(x) for x in ftg_t])][0]
avg_ftg = []
for i in range(max([len(x) for x in ftg_t])):
    sum_f = 0
    n = 0
    for f in ftg_pts:
        if len(f) > i:
            sum_f += f[i]
            n += 1
    if n > 10:
        avg_ftg.append(sum_f / n)
    else:
        avg_ftg.append(avg_ftg[-1])

plt.plot(avg_t, avg_ftg, color='red', linewidth=2.0, label='average')

HUM_SWITCH = 55.0
plt.vlines([HUM_SWITCH], [0.0], [0.2], color='blue', label='hum. switch')
plt.legend()
plt.show()

COMPL_TIMES = [find_last_chg_pt(ftg_t[i], sim) for (i, sim) in enumerate(ftg_pts)]
COMPL_TIMES = [x for x in COMPL_TIMES if x > HUM_SWITCH]
AVG_COMPL_TIME = sum(COMPL_TIMES) / len(COMPL_TIMES)
print('AVG COMPLETION TIME: {}'.format(AVG_COMPL_TIME))

SUCCEEDED_WITHIN_AVG = [sim for (i, sim) in enumerate(ftg_pts) if find_last_chg_pt(ftg_t[i], sim) <= 80.0]
PERC_SUCCESS = len(SUCCEEDED_WITHIN_AVG) / len(ftg_pts)
print('SUCCESS PERCENTAGE: {}'.format(PERC_SUCCESS))

HUM_1_FTG = [f[:ftg_t[i].index(HUM_SWITCH)] for (i, f) in enumerate(ftg_pts) if len(f) > HUM_SWITCH]
EXP_MAX_1 = sum([max(f) for f in HUM_1_FTG]) / len(ftg_pts)
print('HUM.1 MAX EXPECTED FATIGUE: {}'.format(EXP_MAX_1))
HUM_2_FTG = [f[ftg_t[i].index(HUM_SWITCH):] for (i, f) in enumerate(ftg_pts) if len(f) > HUM_SWITCH]
EXP_MAX_2 = sum([max(f) for f in HUM_2_FTG]) / len(ftg_pts)
print('HUM.2 MAX EXPECTED FATIGUE: {}'.format(EXP_MAX_2))

plt.figure(figsize=(10, 5))
chg_t, chg_pts = zip(*[parse_file(s + CHG_FILE) for s in SIM_LOGS_DIRS])
for (i, t) in enumerate(chg_t):
    plt.plot(t, chg_pts[i], color='orange', linewidth=0.5)
plt.show()

MIN_CHG = [c[chg_t[i].index(80)] for (i, c) in enumerate(chg_pts) if len(chg_t[i]) >= 80]
EXP_MIN_CHG = sum(MIN_CHG) / len(MIN_CHG)
print('EXP. MINIMUM CHARGE: {}'.format(EXP_MIN_CHG + 30))
