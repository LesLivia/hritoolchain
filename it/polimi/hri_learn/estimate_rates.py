import mgrs.emg_mgr as emg_mgr
import matplotlib.pyplot as plt


def parse_float(x: str):
    try:
        return float(x)
    except ValueError:
        return None


def line_to_sig(line: str, state: str):
    fields = line.split(':')
    if fields[2] != state:
        return []
    values = fields[3].split('#')
    values = [parse_float(value) for value in values]
    return values


LOG_PATH = 'resources/sim_logs/humanFatigue.log'
SAMPLING_RATE = 1080
INIT_LAMBDA = 0.0005
INIT_MU = 0.0005

f = open(LOG_PATH)
lines = f.readlines()
lines = lines[1:]
signal_mov = []
signal_rest = []
for line in lines:
    signal_mov += line_to_sig(line, 'm')
    signal_rest += line_to_sig(line, 'r')

signal_mov = list(filter(lambda v: v is not None, signal_mov))
signal_rest = list(filter(lambda v: v is not None, signal_rest))

print(signal_mov[:10])
print(signal_rest[:10])

plt.figure(figsize=(10, 5))
plt.plot(signal_mov)
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(signal_rest)
plt.show()

try:
    mnf = emg_mgr.calculate_mnf(signal_mov, SAMPLING_RATE, cf=0)
    b_s, b_e = emg_mgr.get_bursts(signal_mov, SAMPLING_RATE)
    q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, b_e / SAMPLING_RATE, plot=True)
    print(m)
except ValueError:
    print(INIT_LAMBDA)

try:
    mnf = emg_mgr.calculate_mnf(signal_rest, SAMPLING_RATE, cf=0)
    b_s, b_e = emg_mgr.get_bursts(signal_rest, SAMPLING_RATE)
    q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, b_e / SAMPLING_RATE, plot=True)
    print(m)
except ValueError:
    print(INIT_MU)