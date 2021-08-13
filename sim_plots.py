import math

import matplotlib.pyplot as plt
import numpy as np


def scale(v, max_v, min_v):
    if v > 0:
        v = v * 5 / max_v
    else:
        v = v * 1 / min_v

    return v


PLOT_TYPE = "pos"

# LOG CONSTANTS
LOG_PATH = "resources/sim_logs/deployment/"
EXP_ID = "SIM_2021-07-15-09-44-36/"
if PLOT_TYPE == 'en':
    VAR_ID = ["humanFatigue.log", "humanFatigue.log", "robotBattery.log"]
    LABELS = ["Ftg. Hum.", "Ftg. Hum.", "Rob. Battery"]
else:
    VAR_ID = ["humanPosition.log", "humanPosition.log", "robotPosition.log"]
    LABELS = ["Coord.D Hum.ID", "Coord.D Hum.ID", "Coord.D Rob."]
LINE_PREFIX = ['hum', 'hum', '']
LOG_EXT = ".log"

SAVE_PATH = "resources/img/"

# DATA CONSTANTS
ID = ['1', '1', '']
if PLOT_TYPE == 'en':
    COLORS = ['limegreen', 'green', 'orangered']
    MULT_FACTOR = [100, 100, 1]
    Tpoll = [1, 1, 1]
else:
    COLORS = ['blue', 'green', 'firebrick']
    MULT_FACTOR = [1, 1, 1]
    Tpoll = [2, 2, 2]
VREP_X_OFFSET = +8.15
VREP_Y_OFFSET = +3.425

fig = plt.figure(figsize=(15, 7))
plt.xlabel('t [s]', fontsize=24)
if PLOT_TYPE == 'en':
    plt.ylabel('[%]', fontsize=24)
    plt.ylim(0, 100)
    plt.xlim(0, 500)
else:
    plt.ylabel('[m]', fontsize=24)
    plt.ylim(0, 27)
    plt.xlim(0, 500)
plt.xticks(fontsize=23)
plt.yticks(fontsize=24)
plt.grid(linestyle="--")

# Acquire files
if PLOT_TYPE == 'en':
    ftg_file = open(LOG_PATH + EXP_ID + VAR_ID[0])
    lines = ftg_file.readlines()
    ftg_t = [float(line.split(':')[0]) for line in lines if line != '\n']
    ftg_t += list(np.arange(ftg_t[-1], 500.0, 1.0))
    ftg_v = [float(line.split(':')[2]) for line in lines if line != '\n']

    ftg_v1 = []
    ftg_v2 = []
    f_0 = 0.0
    for (i, t) in enumerate(ftg_t):
        if t < 49:
            ftg_v1.append(ftg_v[i] * MULT_FACTOR[0])
            f_0 = ftg_v[i]
        else:
            ftg_v1.append((f_0 * math.exp(-0.003 * (t - 50))) * MULT_FACTOR[0])

        if t < 49:
            ftg_v2.append(0.0)
        else:
            ftg_v2.append((1 - 0.99 * math.exp(-0.01 * (t - 49))) * MULT_FACTOR[0])

    plt.plot(ftg_t, ftg_v1, color=COLORS[0], label=LABELS[0] + '1')
    plt.plot(ftg_t, ftg_v2, color=COLORS[1], label=LABELS[1] + '2')

    chg_file = open(LOG_PATH + EXP_ID + VAR_ID[2])
    lines = chg_file.readlines()
    chg_t = ftg_t  # [float(line.split(':')[0]) for line in lines if line != '\n']
    chg_v = [100 - (100 - 50.0) * math.exp(0.00102 * t) for t in
             chg_t]  # [float(line.split(':')[1]) for line in lines if line != '\n']
    plt.plot(chg_t, [v * MULT_FACTOR[2] for v in chg_v], color=COLORS[2], label=LABELS[2])
else:
    hum_pos_file = open(LOG_PATH + EXP_ID + VAR_ID[0])
    lines = hum_pos_file.readlines()
    lines = [line for line in lines if line != '\n']
    hum_pos_t = [float(line.split(':')[0]) for line in lines]
    hum_pos_x = [float(line.split(':')[2].split('#')[0])+VREP_X_OFFSET for line in lines]
    hum_pos_y = [float(line.split(':')[2].split('#')[1])+VREP_Y_OFFSET for line in lines]
    plt.plot(hum_pos_t, hum_pos_x, color=COLORS[0], label=LABELS[0])
    plt.plot(hum_pos_t, hum_pos_y, '--', color=COLORS[0], label=LABELS[0])

    rob_pos_file = open(LOG_PATH + EXP_ID + VAR_ID[2])
    lines = rob_pos_file.readlines()
    lines = [line for line in lines if line != '\n']
    rob_pos_t = [float(line.split(':')[0]) for line in lines]
    rob_pos_x = [float(line.split(':')[1].split('#')[0])+VREP_X_OFFSET for line in lines]
    rob_pos_y = [float(line.split(':')[1].split('#')[1])+VREP_Y_OFFSET for line in lines]
    plt.plot(rob_pos_t, rob_pos_x, color=COLORS[2], label=LABELS[2])
    plt.plot(rob_pos_t, rob_pos_y, '--', color=COLORS[2], label=LABELS[2])

plt.legend(prop={'size': 20})
plt.savefig(SAVE_PATH + EXP_ID + PLOT_TYPE + '.pdf', figsize=(15, 5))
plt.show()
