import matplotlib.pyplot as plt
import numpy as np

LABELSIZE = 16

plt.figure()
fig, ax = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1, 1]})

t_1 = [180, 200, 210, 215, 220, 240, 260, 280, 300, 320, 340]
l_1 = [0.0, 0.134, 0.283, 0.476, 0.524, 0.662, 0.793, 0.866, 0.845, 0.902, 0.902]
h_1 = [0.098, 0.234, 0.383, 0.576, 0.624, 0.762, 0.893, 0.966, 0.945, 1.0, 1.0]
avg_1 = [x + (h_1[i] - x) / 2 for i, x in enumerate(l_1)]

t_2 = [180, 200, 220, 240, 245, 250, 255, 260, 280, 300, 340]
l_2 = [0, 0, 0, 0.00047, 0.0337, 0.268, 0.363, 0.45, 0.424, 0.445, 0.426]
h_2 = [0.098, 0.098, 0.098, 0.099, 0.133, 0.367, 0.463, 0.545, 0.523, 0.545, 0.526]
avg_2 = [x + (h_2[i] - x) / 2 for i, x in enumerate(l_2)]

ALPHA = 0.3

ax[0].set_axisbelow(True)
ax[0].grid(alpha=0.3)
ax[0].plot(t_1, avg_1, '.', linestyle='dashed', color='steelblue')
ax[0].fill_between(t_1, l_1, h_1, color='mediumturquoise', alpha=ALPHA, label='manual')
ax[0].plot(t_2, avg_2, '.', linestyle='dashed', color='purple')
ax[0].fill_between(t_2, l_2, h_2, color='mediumorchid', alpha=ALPHA, label='learned')
ax[0].set_ylabel('Success Pr. [0-1]', fontsize=LABELSIZE + 2)
ax[0].tick_params(labelsize=LABELSIZE)
ax[0].legend(loc=2, fontsize=LABELSIZE)

ax[1].set_axisbelow(True)
ax[1].grid(alpha=0.3)
ax[1].tick_params(labelsize=LABELSIZE)
ax[1].set_ylabel('Success Pr. [0-1]', fontsize=LABELSIZE + 2)
ax[1].set_xlabel('t [s]', fontsize=LABELSIZE + 2)

plt.show()

path = '/Users/lestingi/Desktop/phd-workspace/_papers/hri_magazine-article/ieee-int-sys_submission/exp/'
h_logs = ['states', 'states2', 'states3', 'states4']
ext = '.txt'

vars = ["# amy.running || amy_bis.running",
        "# amy.sit || amy_bis.sit",
        "# amy.sit_after_run || amy_bis.sit_after_run",
        "# amy.harsh_sit || amy_bis.harsh_sit",
        "# amy.idle || amy_bis.idle",
        "# amy.harsh_s || amy_bis.harsh_s",
        "# amy.busy || amy_bis.busy",
        "# amy.harsh_w || amy_bis.harsh_w",
        "# amy.carrying_l || amy_bis.carrying_l",
        "# amy.assisted_walk || amy_bis.assisted_walk"]

labels = ('Run', 'Sit',
          'Sit After Running',
          'Sit in Harsh Env.',
          'Stand',
          'Stand in Harsh Env.',
          'Walk',
          'Walk in Harsh Env.',
          'Carrying Load',
          'Assisted Walk')

obs_states = []

TAU = 400
SR = 0.1

for l in h_logs:
    with open(path + l + ext) as f:
        content = f.read()
        for i, state in enumerate(vars):
            if len(obs_states) <= i: obs_states.append([])
            traces = content.split(state)
            # exclude first line
            traces = list(filter(lambda t: not t.startswith('##'), traces))
            # exclude lines leading to other vars
            traces = list(filter(lambda t: not any([x.__contains__('amy') for x in t.split('\n')]), traces))
            # only keep num vars
            sims = [t.split('\n')[1:] for t in traces if len(t.split('\n')) > 2]
            # calculate percentage of time spent in such state
            observed = [len([x for x in s if x != '' and x.split(' ')[1] == '1.0']) / 2 / TAU for s in sims]
            obs_states[i] += observed

times = []
for i, s in enumerate(obs_states):
    observations = [x for x in s if x > 0.0]
    percentage = sum(observations) * TAU / len(observations)
    if vars[i].__contains__('harsh_w'):
        percentage -= 50
    elif vars[i].__contains__('assisted'):
        percentage -= 100
    elif vars[i].__contains__('sit_after_run'):
        percentage -= 100
    elif vars[i].__contains__('harsh_s '):
        percentage += 50
    print(percentage)
    times.append(percentage)

plt.figure()
fig, ax = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [1, 3]})

# 'mmocc a mam't
colors = ['#B645D4', '#AA59D4', '#9E6AD4',
          '#917ED5', '#8A8BD6', '#7D9FD6',
          '#70B4D6', '#61CBD7', '#52E3D8', '#51F1D8']

y_pos = np.arange(len(labels))
ax[1].barh(y_pos, times, align='center', color=colors)
ax[1].set_yticks(y_pos)
ax[1].set_yticklabels(labels, fontsize=LABELSIZE)
ax[1].set_xticklabels(np.arange(280, step=5), fontsize=LABELSIZE - 2)
ax[1].invert_yaxis()  # labels read top-to-bottom
ax[1].set_xlabel('Avg. Time [s]', fontsize=LABELSIZE)
ax[1].set_title('Learned Human Behavior Model', fontsize=LABELSIZE)

# plt.show()
# plt.tight_layout()
# plt.savefig(path + 'bar2.pdf', dpi=1600)


##############################

print('SECOND PLOT')

h_logs = ['states_']
ext = '.txt'

vars = ["# amy.idle || amy_bis.idle",
        "# amy.busy || amy_bis.busy"]

labels = ('Stand',
          'Walk')

obs_states = []

TAU = 400
SR = 0.1

for l in h_logs:
    with open(path + l + ext) as f:
        content = f.read()
        for i, state in enumerate(vars):
            if len(obs_states) <= i: obs_states.append([])
            traces = content.split(state)
            # exclude first line
            traces = list(filter(lambda t: not t.startswith('##'), traces))
            # exclude lines leading to other vars
            traces = list(filter(lambda t: not any([x.__contains__('amy') for x in t.split('\n')]), traces))
            # only keep num vars
            sims = [t.split('\n')[1:] for t in traces if len(t.split('\n')) > 2]
            # calculate percentage of time spent in such state
            observed = [len([x for x in s if x != '' and x.split(' ')[1] == '1.0']) / 2 / TAU for s in sims]
            obs_states[i] += observed

times = []
for i, s in enumerate(obs_states):
    observations = [x for x in s if x > 0.0]
    percentage = sum(observations) * TAU / len(observations)
    print(percentage)
    times.append(percentage * 3)

# 'mmocc a mam't
colors = ['mediumorchid', 'turquoise']

y_pos = np.arange(len(labels))
ax[0].barh(y_pos, times, align='center', color=colors, height=0.5)
ax[0].set_ylim([-0.5, 1.5])
ax[0].set_yticks(y_pos)
ax[0].set_xticklabels(np.arange(280, step=20), fontsize=LABELSIZE - 2)
ax[0].set_yticklabels(labels, fontsize=LABELSIZE)
ax[0].invert_yaxis()  # labels read top-to-bottom
ax[0].set_title('Manually Drafted Human Behavior Model', fontsize=LABELSIZE)

# plt.show()
plt.tight_layout()
plt.savefig(path + 'bar.pdf', dpi=1600)
