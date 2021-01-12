import math
from typing import List

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

lambdas = []
step = SAMPLING_RATE * T_POLL
definitive_bursts = []
candidate_bursts = []


def overlaps(burst: List[float], prevs: List[List[float]]):
    for cand in prevs:
        if cand[0] > burst[1]:
            continue
        else:
            return cand

    return None


for i in np.arange(step, len(signal_mov) + step, step):
    start = definitive_bursts[len(definitive_bursts) - 1][1] if len(definitive_bursts) > 0 else 0
    sig = signal_mov[start:int(min(i, len(signal_mov)))]
    try:
        b_s, b_e = emg_mgr.get_bursts(sig, SAMPLING_RATE)
        for (index, b) in enumerate(b_s):
            adj_burst = [b + start, b_e[index] + start]
            best_fit = overlaps(adj_burst, candidate_bursts)
            if best_fit is None:
                candidate_bursts.append(adj_burst)
            elif best_fit is not None:
                definitive_bursts.append(adj_burst)
                candidate_bursts.remove(best_fit)

        bursts_start = [burst[0] for burst in definitive_bursts]
        bursts_end = [burst[1] for burst in definitive_bursts]
        mnf = emg_mgr.calculate_mnf(signal_mov[:int(i)], SAMPLING_RATE, cf=CORRECTION_FACTOR, b_s=bursts_start,
                                    b_e=bursts_end)
        q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, [x / SAMPLING_RATE for x in bursts_end], plot=False)
        if m >= 0:
            raise ValueError
        print('EST LAMBDA: {}'.format(math.fabs(m)))
        lambdas.append(math.fabs(m))
    except ValueError:
        pass

print(definitive_bursts)
bursts_start = [burst[0] for burst in definitive_bursts]
bursts_end = [burst[1] for burst in definitive_bursts]
plt.figure(figsize=(10, 5))
plt.plot(signal_mov, 'gray', linewidth=0.2)
plt.plot(bursts_start, [0] * len(bursts_start), 'g.')
plt.plot(bursts_end, [0] * len(bursts_end), 'r.')
plt.show()

avg_lambda = sum(lambdas) / len(lambdas)
print('FINAL AVG LAMBDA: {:.4f}'.format(avg_lambda))

mus = []
definitive_bursts = []
candidate_bursts = []
for i in np.arange(step, len(signal_mov) + step, step):
    start = definitive_bursts[len(definitive_bursts) - 1][1] if len(definitive_bursts) > 0 else 0
    sig = signal_rest[start:int(min(i, len(signal_mov)))]
    try:
        b_s, b_e = emg_mgr.get_bursts(sig, SAMPLING_RATE)
        for (index, b) in enumerate(b_s):
            adj_burst = [b + start, b_e[index] + start]
            best_fit = overlaps(adj_burst, candidate_bursts)
            if best_fit is None:
                candidate_bursts.append(adj_burst)
            elif best_fit is not None:
                definitive_bursts.append(adj_burst)
                candidate_bursts.remove(best_fit)

        bursts_start = [burst[0] for burst in definitive_bursts]
        bursts_end = [burst[1] for burst in definitive_bursts]
        mnf = emg_mgr.calculate_mnf(signal_rest[:int(i)], SAMPLING_RATE, cf=CORRECTION_FACTOR, b_s=bursts_start,
                                    b_e=bursts_end)
        q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf, [x / SAMPLING_RATE for x in bursts_end], plot=False)
        if m <= 0:
            raise ValueError
        print('EST MU: {}'.format(math.fabs(m)))
        mus.append(math.fabs(m))
    except ValueError:
        pass

print(definitive_bursts)
bursts_start = [burst[0] for burst in definitive_bursts]
bursts_end = [burst[1] for burst in definitive_bursts]
plt.figure(figsize=(10, 5))
plt.plot(signal_rest, 'gray', linewidth=0.2)
plt.plot(bursts_start, [0] * len(bursts_start), 'g.')
plt.plot(bursts_end, [0] * len(bursts_end), 'r.')
plt.show()

avg_mu = sum(mus) / len(mus)
print('FINAL AVG MU: {:.4f}'.format(avg_mu))
