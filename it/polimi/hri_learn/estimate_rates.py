import math

import matplotlib.pyplot as plt
import numpy as np

import mgrs.emg_mgr as emg_mgr


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
T_POLL = 2.0
CORRECTION_FACTOR = 0
INIT_LAMBDA = 0.0005
INIT_MU = 0.0002

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

lambdas = []
for i in np.arange(0, len(signal_mov), SAMPLING_RATE * T_POLL):
    sig = signal_mov[:int(i)]
    try:
        mnf = emg_mgr.calculate_mnf(sig, SAMPLING_RATE, cf=CORRECTION_FACTOR)
        b_s, b_e = emg_mgr.get_bursts(sig, SAMPLING_RATE)
        # plt.plot(sig)
        # plt.plot(b_s, [0] * len(b_s), 'w.')
        # plt.plot(b_e, [0] * len(b_e), 'r.')
        # plt.show()
        q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, b_e / SAMPLING_RATE, plot=False)
        if m >= 0:
            raise ValueError
        print('EST LAMBDA: {}'.format(math.fabs(m)))
        lambdas.append(math.fabs(m))
    except ValueError:
        # print(INIT_LAMBDA)
        lambdas.append(INIT_LAMBDA)

avg_lambda = sum(lambdas) / len(lambdas)
print('FINAL AVG LAMBDA: {:.4f}'.format(avg_lambda))

mus = []
for i in np.arange(0, len(signal_rest), SAMPLING_RATE * T_POLL):
    sig = signal_rest[:int(i)]
    try:
        mnf = emg_mgr.calculate_mnf(sig, SAMPLING_RATE, cf=CORRECTION_FACTOR)
        b_s, b_e = emg_mgr.get_bursts(sig, SAMPLING_RATE)
        # plt.plot(sig)
        # plt.plot(b_s, [0] * len(b_s), 'w.')
        # plt.plot(b_e, [0] * len(b_e), 'r.')
        # plt.show()
        q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, b_e / SAMPLING_RATE, plot=False)
        if m <= 0:
            raise ValueError
        print('EST MU: {}'.format(math.fabs(m)))
        mus.append(math.fabs(m))
    except ValueError:
        # print(INIT_MU)
        mus.append(INIT_MU)

avg_mu = sum(mus) / len(mus)
print('FINAL AVG MU: {:.4f}'.format(avg_mu))
