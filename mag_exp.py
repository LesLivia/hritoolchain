path = '/Users/lestingi/Desktop/phd-workspace/_papers/hri_magazine-article/ieee-int-sys_submission/exp/'
h_logs = ['states', 'states2', 'states3', 'states4']
ext = '.txt'

vars = ["# amy.running || amy_bis.running",
        "# amy.sit || amy_bis.sit",
        "# amy.idle || amy_bis.idle",
        "# amy.busy || amy_bis.busy",
        "# amy.harsh_s || amy_bis.harsh_s",
        "# amy.harsh_sit || amy_bis.harsh_sit",
        "# amy.harsh_w || amy_bis.harsh_w",
        "# amy.sit_after_run || amy_bis.sit_after_run",
        "# amy.assisted_walk || amy_bis.assisted_walk",
        "# amy.carrying_l || amy_bis.carrying_l"]

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
            observed = [len([x for x in s if x != '' and x.split(' ')[1] == '1.0']) / 2 / TAU for s in sims]
            obs_states[i] += observed

for s in obs_states:
    observations = [x for x in s if x > 0.0]
    percentage = sum(observations) * TAU / len(observations)
    print(percentage)
