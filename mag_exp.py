import matplotlib.pyplot as plt
import numpy as np

path = '/Users/lestingi/Desktop/phd-workspace/_papers/hri_magazine-article/ieee-int-sys_submission/exp/'
h_logs = ['states', 'states2', 'states3', 'states4']
ext = '.txt'

vars = ["# amy.running || amy_bis.running",
        "# amy.sit || amy_bis.sit",
        "# amy.idle || amy_bis.idle",
        "# amy.busy || amy_bis.busy",
        "# amy.harsh_w || amy_bis.harsh_w",
        "# amy.sit_after_run || amy_bis.sit_after_run",
        "# amy.assisted_walk || amy_bis.assisted_walk",
        "# amy.carrying_l || amy_bis.carrying_l",
        "# amy.harsh_sit || amy_bis.harsh_sit",
        "# amy.harsh_s || amy_bis.harsh_s"
        ]

labels = ('Run', 'Sit', 'Stand', 'Walk', 'Stand (H)', 'Sit (H)', 'Walk (H)', 'Sit After Running', 'Assisted Walk',
          'Carrying Load')

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
for s in obs_states:
    observations = [x for x in s if x > 0.0]
    percentage = sum(observations) * TAU / len(observations)
    print(percentage)
    times.append(percentage)

plt.figure(figsize=[10, 5])
fig, ax = plt.subplots()

# 'mmocc a mam't
colors = ['#B645D4', '#AA59D4', '#9E6AD4',
          '#917ED5', '#8A8BD6', '#7D9FD6',
          '#70B4D6', '#61CBD7', '#52E3D8', '#51F1D8']

y_pos = np.arange(len(labels))
ax.barh(y_pos, times, align='center', color=colors)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Avg. Time [s]')

plt.show()
