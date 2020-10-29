import matplotlib.pyplot as plt
from typing import List


def scale(v, max_v, min_v):
    if v > 0:
        v = v * 5 / max_v
    else:
        v = v * 1 / min_v

    return v


PLOT_TYPE = "pos"

# LOG CONSTANTS
LOG_PATH = "resources/sim_logs/"
EXP_ID = "exp4/"
if PLOT_TYPE == 'en':
    VAR_ID = ["humanFatigue", "humanFatigue", "robotBattery"]
else:
    VAR_ID = ["humanPosition", "humanPosition", "robotPosition"]
LINE_PREFIX = ['hum', 'hum', '']
LOG_EXT = ".log"

SAVE_PATH = "resources/img/"

# DATA CONSTANTS
ID = ['1', '2', '']
if PLOT_TYPE == 'en':
    COLORS = ['limegreen', 'green', 'orangered']
    MULT_FACTOR = [13.75, 10, 0.1]
    Tpoll = [4, 4, 4]
else:
    COLORS = ['blue', 'navy', 'firebrick']
    MULT_FACTOR = [1, 1, 1]
    Tpoll = [2, 2, 2]
VREP_X_OFFSET = +8.15
VREP_Y_OFFSET = +3.425

fig = plt.figure(figsize=(30, 7))
plt.xlabel('t [s]', fontsize=24)
if PLOT_TYPE == 'en':
    plt.ylabel('[%]', fontsize=24)
else:
    plt.ylabel('[m]', fontsize=24)
plt.xticks(fontsize=23)
plt.yticks(fontsize=24)
plt.grid(linestyle="--")

# Acquire files
for i in range(0, len(VAR_ID)):
    f = open(LOG_PATH + EXP_ID + VAR_ID[i] + LOG_EXT, "r")
    lines = f.readlines()
    if LINE_PREFIX[i] != '':
        lines = list(filter(lambda l: l.startswith(LINE_PREFIX[i] + ID[i]), lines))
    else:
        lines = list(filter(lambda l: len(l) > 1, lines))

    x = range(0, len(lines) * Tpoll[i], Tpoll[i])
    if PLOT_TYPE == 'en':
        y: List[float] = []
    else:
        y_x: List[float] = []
        y_y: List[float] = []

    for line in lines:
        if len(line.split(":")) > 1:
            if PLOT_TYPE == 'en':
                value = line.split(":")[1]
            else:
                value_x = line.split(":")[1].split("#")[0]
                value_y = line.split(":")[1].split("#")[1]
        else:
            if PLOT_TYPE == 'en':
                value = line
            else:
                value_x = line.split('#')[0]
                value_y = line.split('#')[1]

        if PLOT_TYPE == 'en':
            y.append(float(value) * MULT_FACTOR[i])
        else:
            y_x.append((float(value_x) + VREP_X_OFFSET) * MULT_FACTOR[i])
            y_y.append((float(value_y) + VREP_Y_OFFSET) * MULT_FACTOR[i])

    f.close()
    if PLOT_TYPE == 'en':
        print(y)
        plt.plot(x, y, color=COLORS[i], label=VAR_ID[i] + ID[i])
    else:
        print(y_x)
        max_y = max(y_y)
        min_y = min(y_y)
        y_y = list(map(lambda v: scale(v, max_y, min_y), y_y))
        print(y_y)
        plt.plot(x, y_x, color=COLORS[i], label=VAR_ID[i] + 'X' + ID[i])
        plt.plot(x, y_y, linestyle='-.', color=COLORS[i], label=VAR_ID[i] + 'Y' + ID[i])

plt.legend(prop={'size': 20})
plt.savefig(SAVE_PATH + EXP_ID + PLOT_TYPE + '.pdf', figsize=(30, 7))
plt.show()
