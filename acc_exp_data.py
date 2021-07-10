import os
import matplotlib.pyplot as plt


def parse_file(path: str):
    f = open(path)
    lines = f.readlines()
    # 1.00: hum1:0.00099700449550337
    # 1.00: 29.9286
    t = [float(line.split(':')[0]) for line in lines if line != '\n']
    vals = [float(line.split(':')[-1]) for line in lines if line != '\n']
    pts = [(x, vals[i]) for (i, x) in enumerate(t)]
    return t, vals


LOG_DIR = "/Users/lestingi/Desktop/logs/sim_logs"
SIM_LOGS_DIRS = [x[0] for x in os.walk(LOG_DIR)]
SIM_LOGS_DIRS = list(filter(lambda x: x.startswith(LOG_DIR + '/SIM_2021-07'), SIM_LOGS_DIRS))

FTG_FILE = '/humanFatigue.log'
CHG_FILE = '/robotBattery.log'
OUT_FILE = '/outfile.txt'

print('FOUND {} SIMULATION TO ANALYZE'.format(len(SIM_LOGS_DIRS)))

### PLOT FTG CURVES

plt.figure()

for sim in SIM_LOGS_DIRS:
    ftg_t, ftg_pts = parse_file(sim + FTG_FILE)
    plt.plot(ftg_t, ftg_pts)

plt.show()

plt.figure()

for sim in SIM_LOGS_DIRS:
    chg_t, chg_pts = parse_file(sim + CHG_FILE)
    plt.plot(chg_t, chg_pts)

plt.show()
