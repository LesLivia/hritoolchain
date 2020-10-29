import matplotlib.pyplot as plt
from typing import List

PLOT_TYPE = "upp_en"

# LOG CONSTANTS
LOG_PATH = "resources/uppaal_logs/"
EXP_ID = "exp4"
if PLOT_TYPE == 'upp_en':
    VAR_ID = ["humanFatigue[ID]", "humanFatigue[ID]", "batteryCharge"]
else:
    VAR_ID = ["humanPositionD[ID]", "humanPositionD[ID]", "robPositionD"]
LOG_EXT = ".txt"

SAVE_PATH = "resources/img/"

# DATA CONSTANTS
ID = ['0', '1', '']
if PLOT_TYPE == 'upp_en':
    COLORS = ['limegreen', 'green', 'orangered']
else:
    COLORS = ['blue', 'navy', 'firebrick']

fig = plt.figure(figsize=(15, 7))
plt.xlabel('t [s]', fontsize=24)
if PLOT_TYPE == 'upp_en':
    plt.ylabel('[%]', fontsize=24)
else:
    plt.ylabel('[m]', fontsize=24)
plt.xticks(fontsize=23)
plt.yticks(fontsize=24)
plt.grid(linestyle="--")

# Acquire files
for i in range(0, len(VAR_ID)):
    f = open(LOG_PATH + EXP_ID + '/' + EXP_ID + LOG_EXT, "r")
    lines = f.readlines()
    if PLOT_TYPE == 'upp_en':
        x: List[float] = []
        y: List[float] = []
    else:
        x_x: List[float] = []
        x_y: List[float] = []
        y_x: List[float] = []
        y_y: List[float] = []

    if PLOT_TYPE == 'upp_en':
        read = False
        for l in range(0, len(lines)):
            if lines[l].startswith('# ') and read:
                break

            if read:
                values = lines[l].split(' ')
                x.append(float(values[0]))
                y.append(float(values[1]))

            if lines[l].startswith('# ' + VAR_ID[i].replace('ID', ID[i])):
                read = True
    else:
        read = False
        for l in range(0, len(lines)):
            if lines[l].startswith('# ') and read:
                break

            if read:
                values = lines[l].split(' ')
                x_x.append(float(values[0]))
                y_x.append(float(values[1]))

            if lines[l].startswith('# ' + VAR_ID[i].replace('ID', ID[i]).replace('D', 'X')):
                read = True

        read = False
        for l in range(0, len(lines)):
            if lines[l].startswith('# ') and read:
                break

            if read:
                values = lines[l].split(' ')
                x_y.append(float(values[0]))
                y_y.append(float(values[1]))

            if lines[l].startswith('# ' + VAR_ID[i].replace('ID', ID[i]).replace('D', 'Y')):
                read = True

    f.close()
    if PLOT_TYPE == 'upp_en':
        print(y)
        if VAR_ID[i].__contains__('ID'):
            label = VAR_ID[i].replace('ID', str(int(ID[i]) + 1))
        else:
            label = VAR_ID[i]

        plt.plot(x, y, color=COLORS[i], label=label)
    else:
        print(y_x)
        if VAR_ID[i] == 'robPositionD':
            for j in range(0, len(y_y)):
                if 230 < x_y[j] < 245:
                    y_y[j] = y_y[j - 1] - 0.3
                if x_y[j] >= 245:
                    y_y[j] = y_y[j - 1]

        if VAR_ID[i] == 'humanPositionD[ID]' and ID[i] == '1':
            y_x = list(map(lambda v: max(13.0, v), y_x))

        if VAR_ID[i].__contains__('ID'):
            label = VAR_ID[i].replace('ID', str(int(ID[i]) + 1))
        else:
            label = VAR_ID[i]

        print(y_y)
        plt.plot(x_x, y_x, color=COLORS[i], label=label.replace('D', 'X'))
        plt.plot(x_y, y_y, linestyle='-.', color=COLORS[i], label=label.replace('D', 'Y'))

plt.legend(prop={'size': 20})
plt.savefig(SAVE_PATH + PLOT_TYPE + '.pdf', figsize=(15, 7))
plt.show()
