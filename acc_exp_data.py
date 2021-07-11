import os
import matplotlib.pyplot as plt


def parse_file(path: str):
    f = open(path)
    lines = f.readlines()
    # 1.00: hum1:0.00099700449550337
    # 1.00: 29.9286
    t = [float(line.split(':')[0]) for line in lines if line != '\n']
    vals = [float(line.split(':')[-1]) for line in lines if line != '\n']
    return t, vals


LOG_DIR = "/Users/lestingi/Desktop/logs/sim_logs"
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

HUM_SWITCH = 51.0
plt.vlines([HUM_SWITCH], [0.0], [0.02], color='blue', label='hum. switch')
plt.legend()
plt.show()

MAX_EXP_1 = max(avg_ftg[:avg_t.index(HUM_SWITCH)])
print('HUM.1 MAX EXPECTED FATIGUE: {}'.format(MAX_EXP_1))
MAX_EXP_2 = max(avg_ftg[avg_t.index(HUM_SWITCH):])
print('HUM.2 MAX EXPECTED FATIGUE: {}'.format(MAX_EXP_2))

plt.figure(figsize=(10, 5))
for sim in SIM_LOGS_DIRS:
    chg_t, chg_pts = parse_file(sim + CHG_FILE)
    plt.plot(chg_t, chg_pts, color='orange', linewidth=0.5)
plt.show()
