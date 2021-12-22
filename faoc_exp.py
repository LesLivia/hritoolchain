import os
import matplotlib.pyplot as plt
import numpy as np
import math


def avg_error(f1, f2):
    sum = 0
    for (i, x) in enumerate(f1):
        sum += math.fabs(x - f2[i]) / x * 100
    return sum / len(f1)


LOGS_PATH = '/Users/lestingi/Desktop/logs/sim_logs/faoc_exp/'
EXP = 'exp2_hl'
N_H = 1

logs = os.listdir(LOGS_PATH + EXP)
logs = list(filter(lambda l: l.startswith('SIM'), logs))
logs.sort()

# SCS plot
plt.figure(figsize=(10, 5))
plt.xticks(np.arange(90, step=10))
plt.yticks(np.arange(1.0, step=1.0))
for sim in logs:
    with open(LOGS_PATH + EXP + '/' + sim + '/humansServed.log') as svdlog:
        lines = svdlog.readlines()
        svdlines = list(filter(lambda l: l.__contains__('served'), lines))
        if len(svdlines) == N_H:
            scstime = float(svdlines[-1].split(':')[0])
            step = [0.0] * len(np.arange(scstime)) + [1.0] * len(np.arange(scstime, 90))
            if len(step)<91:
                step.append(1.0)
            plt.plot(np.arange(91), step, linewidth=0.5, color='grey')
plt.show()

# FTG plot
plt.figure(figsize=(10, 5))
plt.xticks(np.arange(90, step=10))
plt.yticks(np.arange(0.05, step=0.01))
for sim in logs:
    with open(LOGS_PATH + EXP + '/' + sim + '/humanFatigue.log') as ftglog:
        lines = ftglog.readlines()
        t = [float(l.split(':')[0]) for l in lines if len(l) > 1]
        ftg = [float(l.split(':')[2]) for l in lines if len(l) > 1]
        plt.plot(t, ftg, linewidth=0.5, color='grey')
plt.ylim([0, 0.015])
plt.show()

# CHG plot
plt.figure(figsize=(10, 5))
plt.xticks(np.arange(90000, step=1000))
plt.yticks(np.arange(13, step=0.5))
t = [0.0]
chg = [11.0]
for sim in logs:
    with open(LOGS_PATH + EXP + '/' + sim + '/robotBattery.log') as chglog:
        lines = chglog.readlines()
        if logs.index(sim) == 0:
            start = float(lines[0].split(':')[0])
        t += [float(l.split(':')[0]) - start for l in lines if len(l) > 1]
        # x/100*0.9+11.1 = float(data.voltage)
        chg += [float(l.split(':')[1]) / 100 * 0.9 + 11.1 for l in lines if len(l) > 1]
# plt.xlim([15000, 21000])
plt.plot(t, chg, linewidth=0.5, color='grey')
plt.plot(t, [11.1] * len(t), color='red')
plt.show()

t_1 = t.copy()
chg_1 = chg.copy()
start = [i for i, x in enumerate(t_1) if x >= 14000][0]
end = [i for i, x in enumerate(t_1) if x <= 27000][-1]
plt.figure(figsize=(10, 5))
with open('/Users/lestingi/Desktop/logs/robotBattery.log', 'r') as full_chg_log:
    data = [(float(l.split(':')[0]) - 1637841295, float(l.split(':')[1])) for l in full_chg_log.readlines() if
            float(l.split(':')[0]) >= 1637841295]
    t = [d[0] for d in data]
    chg = [d[1] for d in data]
    plt.plot([x / 60 for x in t], chg, linewidth=.5, color='grey')
    z = np.polyfit(t, chg, 3)
    print(z)
    f = np.poly1d(z)
    plt.plot([x / 60 for x in t], f(t), color='red')
    for i in range(10):
        z = np.polyfit(t, chg, i)
        f = np.poly1d(z)
        print('Avg. error with curve of order {}: {}'.format(i, avg_error(chg, f(t))))
        # plt.plot([x / 60 for x in t], f(t))
    # plt.plot([x / 60 for x in t], [z[3] + z[2] * x + z[1] * x**2 + z[0] * x**3 for x in t])
plt.plot([(x - t_1[start]) / 60 for x in t_1[start:end]], [x for x in chg_1[start:end]])
z_1 = np.polyfit([x - t_1[start] for x in t_1[start:end]], [c for c in chg_1[start:end]], 3)
print(z_1)
f_1 = np.poly1d(z_1)
plt.plot([(x - t_1[start]) / 60 for x in t_1[start:end]], f_1([x - t_1[start] for x in t_1[start:end]]), color='red')
# plt.show()

for i in range(10):
    z_1 = np.polyfit([x - t_1[start] for x in t_1[start:end]], chg_1[start:end], i)
    f_1 = np.poly1d(z_1)
    err = avg_error(chg_1[start:end], f_1([x - t_1[start] for x in t_1[start:end]]))
    print('Avg. error with curve of order {}: {}'.format(i, err))

with open('/Users/lestingi/Desktop/logs/new_cycle/robotBattery.log', 'r') as chglog:
    data = [l for l in chglog.readlines() if len(l) > 1 and (l.startswith('voltage') or l.__contains__(' secs'))]
    t = [float(l.split(':')[1]) for l in data if l.__contains__(' secs')]
    chg = [float(l.split(':')[1]) for l in data if l.__contains__('voltage')]
    # plt.figure()
    z = np.polyfit([(x - t[0]) for x in t], chg, 3)
    print(z)
    f = np.poly1d(z)
    plt.plot([(x - t[0]) / 60 for x in t], chg)
    plt.show()
