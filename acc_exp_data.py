import matplotlib.pyplot as plt
import numpy as np

x = [2, 3, 4, 4, 7]
y = [18, 1 * 60 + 30, 3 * 60 + 55, 2 * 60 + 22, 17 * 60 + 27]
traces = [140, 304, 788, 607, 2742]
colors = ['lightcoral', 'indianred', 'firebrick', 'firebrick', 'maroon']
colors_traces = ['peachpuff', 'sandybrown', 'chocolate', 'chocolate', 'saddlebrown']

plt.figure(figsize=[10, 5])
plt.grid(color='lightgrey', zorder=0)
plt.xlabel('No. of Locations', fontsize=15)
plt.ylabel('Learning Time [s]', fontsize=15)
plt.xticks(x, fontsize=15, fontweight='bold')
plt.yticks(np.arange(0, 1100, 200), fontsize=15, fontweight='bold')
plt.plot(x, y, 'k--', zorder=4, linewidth=2)
plt.plot(x, y, '.', markersize=20, color='black', zorder=5)
plt.bar(x, y, zorder=3, color=colors, width=.5)
plt.show()

plt.figure(figsize=[10, 5])
plt.grid(color='lightgrey', zorder=0)
plt.xlabel('No. of Locations', fontsize=15)
plt.ylabel('No. of Sampled Traces', fontsize=15)
plt.xticks(x, fontsize=15, fontweight='bold')
plt.yticks(np.arange(0, max(traces), 500), fontsize=15, fontweight='bold')
plt.plot(x, traces, 'k--', zorder=4)
plt.plot(x, traces, '.', markersize=20, color='black', zorder=5)
plt.bar(x, traces, zorder=3, color=colors_traces, width=.5)
plt.show()

x = [2, 3, 4, 10]
y = [41, 60 + 2, 3 * 60 + 1, 37 * 60 + 88]
traces = [154, 356, 681, 5497]
colors = ['lightcoral', 'indianred', 'firebrick', 'maroon']
colors_traces = ['peachpuff', 'sandybrown', 'chocolate', 'saddlebrown']

plt.figure(figsize=[10, 5])
plt.grid(True, color='lightgrey', zorder=0)
plt.xlabel('No. of Locations', fontsize=15)
plt.ylabel('Learning Time [s]', fontsize=15)
plt.xticks(x, fontsize=15, fontweight='bold')
plt.yticks(np.arange(0, max(y), 500), fontsize=15, fontweight='bold')
plt.plot(x, y, 'k--', zorder=4, linewidth=2)
plt.plot(x, y, '.', markersize=20, color='black', zorder=5)
plt.bar(x, y, zorder=3, color=colors)
plt.show()

plt.figure(figsize=[10, 5])
plt.grid(color='lightgrey')
plt.xlabel('No. of Locations', fontsize=15)
plt.ylabel('No. of Sampled Traces', fontsize=15)
plt.xticks(x, fontsize=15, fontweight='bold')
plt.yticks(np.arange(0, max(traces), 1000), fontsize=15, fontweight='bold')
plt.plot(x, traces, 'k--', linewidth=2, zorder=4)
plt.plot(x, traces, '.', markersize=20, color='black', zorder=5)
plt.bar(x, traces, zorder=3, color=colors)
plt.bar(x, traces, zorder=3, color=colors_traces)
plt.show()

# t = np.arange(0, 600, 0.1)
# chg_pts = [60, 270, 380, 530]
# labels = ['turn_on', 'turn_off', 'open', 'close']
#
# fig = plt.figure(figsize=(10, 5))
#
# F = [37 - (37 - 36.5) * math.exp(-0.005 * i) for i in t if i <= chg_pts[0]]
# F = F + [F[-1] * math.exp(-0.00007 * (i - chg_pts[0])) for i in t if chg_pts[0] < i <= chg_pts[1]]
# F = F + [37 - (37 - F[-1]) * math.exp(-0.005 * (i - chg_pts[1])) for i in t if chg_pts[1] < i <= chg_pts[2]]
# F = F + [F[-1] * math.exp(-0.00005 * (i - chg_pts[2])) for i in t if chg_pts[2] < i <= chg_pts[3]]
# F = F + [37 - (37 - F[-1]) * math.exp(-0.005 * (i - chg_pts[3])) for i in t if chg_pts[3] < i]
#
# plt.xlim(t[0], t[-1])
# plt.ylim(36, 36.8)
# plt.xticks([0] + chg_pts + [600], fontsize=15)
# plt.yticks(np.arange(36, 36.8, 0.1), fontsize=15)
# plt.xlabel('t [s]', fontsize=18)
# plt.ylabel('temp [°C]', fontsize=18)
# plt.plot(t, F, 'k--', linewidth=1)
#
# start_segm = np.where(t == chg_pts[2])[0][0]
# end_segm = np.where(t == chg_pts[3])[0][0]
# plt.plot(t[start_segm:end_segm], F[start_segm:end_segm], 'blue', linewidth=3)
#
# plt.vlines(chg_pts, [36] * len(chg_pts), [36.7] * len(chg_pts), linewidth=1.5)
# plt.vlines(chg_pts[2], [36] * len(chg_pts), [36.7] * len(chg_pts), color='springgreen', linewidth=3)
# plt.vlines(chg_pts[3], [36] * len(chg_pts), [36.7] * len(chg_pts), color='r', linewidth=3)
#
# vert_t = np.arange(0, 600, 10)
# vert_F = [37 - (37 - 36.5) * math.exp(-0.005 * i) for i in vert_t if i <= chg_pts[0]]
# vert_F = vert_F + [vert_F[-1] * math.exp(-0.00007 * (i - chg_pts[0])) for i in vert_t if chg_pts[0] < i <= chg_pts[1]]
# vert_F = vert_F + [37 - (37 - vert_F[-1]) * math.exp(-0.005 * (i - chg_pts[1])) for i in vert_t if
#                    chg_pts[1] < i <= chg_pts[2]]
# vert_F = vert_F + [vert_F[-1] * math.exp(-0.00005 * (i - chg_pts[2])) for i in vert_t if chg_pts[2] < i <= chg_pts[3]]
# vert_F = vert_F + [37 - (37 - vert_F[-1]) * math.exp(-0.005 * (i - chg_pts[3])) for i in vert_t if chg_pts[3] < i]
#
# plt.vlines(vert_t, [36] * len(vert_F), vert_F, linewidth=.25)
#
# for (i, label) in enumerate(labels):
#     plt.text(chg_pts[i] - 20, 36.725, label, rotation=0, fontsize=15)
#     plt.plot(chg_pts[i], 36.7, 'k.', markersize=10)
#     # plt.plot(chg_pts[i], F[np.where(t == chg_pts[i])[0][0]], 'kx', mew=3, markersize=15)
# # plt.show()
#
# plt.tight_layout()
# plt.savefig('segment_example.pdf', dpi=300, transparent=True)
#
#
# def parse_file(path: str):
#     f = open(path)
#     lines = f.readlines()
#     # 1.00: hum1:0.00099700449550337
#     # 1.00: 29.9286
#     t = [float(line.split(':')[0]) for line in lines if line != '\n']
#     vals = [float(line.split(':')[-1]) for line in lines if line != '\n']
#     return t, vals
#
#
# def find_last_chg_pt(t: List[float], v: List[float]):
#     for i in range(len(v) - 1, 1, -1):
#         if v[i] > v[i - 1]:
#             return t[i - 1]
#     else:
#         return 0.0
#
#
# LOG_DIR = "/Users/lestingi/PycharmProjects/hritoolchain/resources/sim_logs/refinement/sit-and-run"
# SIM_LOGS_DIRS = [x[0] for x in os.walk(LOG_DIR)]
# SIM_LOGS_DIRS = list(filter(lambda x: x.startswith(LOG_DIR + '/SIM_2021-06'), SIM_LOGS_DIRS))
#
# FTG_FILE = '/humanFatigue.log'
# CHG_FILE = '/robotBattery.log'
# OUT_FILE = '/outfile.txt'
#
# print('FOUND {} SIMULATION TO ANALYZE'.format(len(SIM_LOGS_DIRS)))
#
# # PLOT FTG CURVES
#
# ftg_t, ftg_pts = zip(*[parse_file(s + FTG_FILE) for s in SIM_LOGS_DIRS])
#
# plt.figure(figsize=(10, 5))
# plt.xlabel('t[s]', fontsize=18)
# plt.ylabel('F[0-1]', fontsize=18)
#
# for (i, t) in enumerate(ftg_t):
#     if i == 0:
#         plt.plot(t, ftg_pts[i], '--', color='black', linewidth=0.25, alpha=0.5,
#                  label='simulations ({})'.format(len(SIM_LOGS_DIRS)))
#     else:
#         plt.plot(t, ftg_pts[i], '--', color='black', linewidth=0.25, alpha=0.5)
#
# avg_t = [t for t in ftg_t if len(t) == max([len(x) for x in ftg_t])][0]
# avg_ftg = []
# for i in range(max([len(x) for x in ftg_t])):
#     sum_f = 0
#     n = 0
#     for f in ftg_pts:
#         if len(f) > i:
#             sum_f += f[i]
#             n += 1
#     if n > 10:
#         avg_ftg.append(sum_f / n)
#     else:
#         avg_ftg.append(avg_ftg[-1])
#
# plt.plot(avg_t, avg_ftg, color='red', linewidth=2.0, label='average')
#
# HUM_SWITCH = 55.0
# plt.vlines([HUM_SWITCH], [0.0], [0.2], color='blue', label='hum. switch')
# plt.legend()
# plt.show()
#
# COMPL_TIMES = [find_last_chg_pt(ftg_t[i], sim) for (i, sim) in enumerate(ftg_pts)]
# COMPL_TIMES = [x for x in COMPL_TIMES if x > HUM_SWITCH]
# AVG_COMPL_TIME = sum(COMPL_TIMES) / len(COMPL_TIMES)
# print('AVG COMPLETION TIME: {}'.format(AVG_COMPL_TIME))
#
# SUCCEEDED_WITHIN_AVG = [sim for (i, sim) in enumerate(ftg_pts) if find_last_chg_pt(ftg_t[i], sim) <= 80.0]
# PERC_SUCCESS = len(SUCCEEDED_WITHIN_AVG) / len(ftg_pts)
# print('SUCCESS PERCENTAGE: {}'.format(PERC_SUCCESS))
#
# HUM_1_FTG = [f[:ftg_t[i].index(HUM_SWITCH)] for (i, f) in enumerate(ftg_pts) if len(f) > HUM_SWITCH]
# EXP_MAX_1 = sum([max(f) for f in HUM_1_FTG]) / len(ftg_pts)
# print('HUM.1 MAX EXPECTED FATIGUE: {}'.format(EXP_MAX_1))
# HUM_2_FTG = [f[ftg_t[i].index(HUM_SWITCH):] for (i, f) in enumerate(ftg_pts) if len(f) > HUM_SWITCH]
# EXP_MAX_2 = sum([max(f) for f in HUM_2_FTG]) / len(ftg_pts)
# print('HUM.2 MAX EXPECTED FATIGUE: {}'.format(EXP_MAX_2))
#
# plt.figure(figsize=(10, 5))
# chg_t, chg_pts = zip(*[parse_file(s + CHG_FILE) for s in SIM_LOGS_DIRS])
# for (i, t) in enumerate(chg_t):
#     plt.plot(t, chg_pts[i], color='orange', linewidth=0.5)
# plt.show()
#
# MIN_CHG = [c[chg_t[i].index(80)] for (i, c) in enumerate(chg_pts) if len(chg_t[i]) >= 80]
# EXP_MIN_CHG = sum(MIN_CHG) / len(MIN_CHG)
# print('EXP. MINIMUM CHARGE: {}'.format(EXP_MIN_CHG + 30))
