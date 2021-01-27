import math

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import mgrs.emg_mgr as emg_mgr

PATH = 'resources/hrv_pg/dryad_data/dump/y5/trial{}.txt'
FTG_TRIAL = '1'
REC_TRIAL = '3'
SAMPLING_RATE = 1080

FIG_SIZE = (30, 9)
DPI = 1000

f = open(PATH.format(FTG_TRIAL))
lines = f.readlines()
t_ftg = [float(line.split('\t')[0]) for line in lines]
y_ftg = [float(line.split('\t')[1]) for line in lines]
f.close()

f = open(PATH.format(REC_TRIAL))
lines = f.readlines()
t_rec = [float(line.split('\t')[0]) + t_ftg[-1] for line in lines]
y_rec = [float(line.split('\t')[1]) for line in lines]
f.close()

t = t_ftg + t_rec
y = y_ftg + y_rec

matplotlib.rcParams['agg.path.chunksize'] = 10000
plt.rc('legend', fontsize=22)
fig, ax = plt.subplots(3, 1, figsize=FIG_SIZE, dpi=DPI)
for i in ax:
    i.tick_params(axis='both', which='major', labelsize=20)

x_ticks = list(np.arange(t[0], t[-1], 100))
x_ticks[3] = t_rec[0]
x_ticks.append(t[-1])
ax[0].set_xticks(ticks=x_ticks)
ax[0].set_xlim(t[0], t[-1])
ax[0].set_ylim(min(y), max(y))
p1 = ax[0].plot(t, y, color='#333333', linewidth=0.1)
ax[0].vlines([t_rec[0]], [min(y)], [max(y)], colors='black', linestyles='dashed')
ax[0].legend((p1), ('EMG signal',), loc='lower right', shadow=False)

b_s_ftg, b_e_ftg = emg_mgr.get_bursts(y_ftg, SAMPLING_RATE)
mnf_ftg = emg_mgr.calculate_mnf(y_ftg, SAMPLING_RATE, cf=0.0001, b_s=b_s_ftg, b_e=b_e_ftg)
q, m, x, est_values = emg_mgr.mnf_lin_reg(mnf_ftg, b_e_ftg / SAMPLING_RATE, plot=False)

b_s_rec, b_e_rec = emg_mgr.get_bursts(y_rec, SAMPLING_RATE)
mnf_rec = emg_mgr.calculate_mnf(y_rec, SAMPLING_RATE, cf=-0.0001, b_s=b_s_rec, b_e=b_e_rec)
q_rec, m_rec, x_rec, est_values_rec = emg_mgr.mnf_lin_reg(mnf_rec, b_e_rec / SAMPLING_RATE, plot=False)

ax[1].set_xticks(ticks=x_ticks)
ax[1].set_xlim(t[0], t[-1])
ax[1].set_ylim(min(mnf_ftg), max(mnf_ftg))
p2, p3 = ax[1].plot(b_e_ftg / SAMPLING_RATE, mnf_ftg, 'k--',
                    [x / SAMPLING_RATE + t_ftg[-1] for x in b_e_rec],
                    [y - (est_values_rec[0] - est_values[-1]) for y in mnf_rec], 'k--',
                    linewidth=.5)
p4, p5 = ax[1].plot(x, est_values, 'k',
                    [i + t_ftg[-1] for i in x_rec],
                    [y - (est_values_rec[0] - est_values[-1]) for y in est_values_rec], 'k',
                    linewidth=1)
ax[1].vlines([t_rec[0]], [min(mnf_ftg)], [max(mnf_ftg)], colors='black', linestyles='dashed')
ax[1].legend((p2, p4), ('ln(f_mean))', 'regression line',), loc='lower right', shadow=False)

ftg = [1 - math.exp(-abs(m) * x) for x in t_ftg]
rec = [ftg[-1] * math.exp(-abs(m_rec) * (x - t_ftg[-1])) for x in t_rec]

ax[2].set_xticks(ticks=x_ticks)
ax[2].set_xlabel('t [s]', fontsize=24, weight='bold')
ax[2].set_xlim(t[0], t[-1])
ax[2].set_ylim(min(ftg), max(ftg) * 1.1)
p6 = ax[2].plot(t_ftg, ftg, 'k', t_rec, rec, 'k', linewidth=1)
ax[2].vlines([t_rec[0]], [min(ftg)], [max(ftg)], colors='black', linestyles='dashed')
ax[2].legend((p6), ('Fatigue',), loc='lower right', shadow=False)

plt.tight_layout()
plt.savefig('/Users/lestingi/Desktop/phd-workspace/_papers/RA-L_IROS21/ieeeconf/figs/emg_plots.pdf', dpi=DPI)
