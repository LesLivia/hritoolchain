import math
import warnings
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

import mgrs.sig_mgr as sig_mgr
import pltr.ha_pltr as ha_pltr
from domain.hafeatures import LocLabels, Location, Edge, HybridAutomaton
from domain.sigfeatures import SignalPoint, TimeInterval, Event


def find_chg_pts(values: List[float]):
    chg_pts: List[int] = []
    prev = values[0]
    for i in range(1, len(values)):
        curr = values[i]
        if curr != prev:
            chg_pts.append(i)
        prev = curr
    return chg_pts


IGNORED_EVENTS = ['enter_area_2']


def find_ignored(values: List[float]):
    # TODO: PROTOTYPE! should work for list of events
    ign_events = []
    for i in range(len(values)):
        if values[i] > 4000.0 >= values[i - 1]:
            ign_events.append(i)
    return ign_events


'''
INITIAL HA
'''
IDLE_LOC = Location('r_0', 'F = f_rest(t)')
BUSY_LOC = Location('w_0', 'F = f_walk(t) <br/> and F &lt;= 1')
FAINT_LOC = Location('faint', 'F = 1')
e_1 = Edge(IDLE_LOC, BUSY_LOC, sync='start_h_action?')
e_2 = Edge(BUSY_LOC, IDLE_LOC, sync='stop_h_action?')
e_3 = Edge(BUSY_LOC, FAINT_LOC, guard='F &gt;= 1')

LOC = [IDLE_LOC, BUSY_LOC, FAINT_LOC]
EDGES = [e_1, e_2, e_3]

HUMAN_FOLLOWER_HA = HybridAutomaton(LOC, EDGES)

ha_pltr.plot_ha(HUMAN_FOLLOWER_HA, 'human_follower', view=True)

'''
START LEARNING PROCEDURE
'''

warnings.filterwarnings('ignore')

LOG_PATH = 'resources/uppaal_logs/test.txt'

'''
PARSE TRACES
'''
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hIdle = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.idle')]

'''
IDENTIFY CHANGE POINTS
(FIRST OVERLAY: HUMAN MOVE)
'''

ftg_entries = []
mov_entries = []
idle_entries = []
chg_pts = []
for (i, sim) in enumerate(ftg):
    entries = sim.split('\n')[1:]
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    ftg_entries.append(entries)

    entries = hMov[i].split('\n')[1:]
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    mov_entries.append(entries)

    entries = hIdle[i].split('\n')[1:]
    entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    idle_entries.append(entries)

    chg_pts.append(find_chg_pts([float(x.split(' ')[1]) for x in mov_entries[i] if len(x.split(' ')) > 1]))

'''
SPLIT SEGMENTS AND SET LABEL
'''
segments = []
labels = []
EVENTS = []
for i in range(len(chg_pts)):
    sim_segm = []
    sim_labels = []
    sim_events = []
    prev = 0.0
    t = [float(x.split(' ')[0]) for x in idle_entries[i][1:len(idle_entries[i]) - 1] if len(x.split(' ')) > 1]

    # one segment for each chg point
    for pt in chg_pts[i]:
        curr = float(mov_entries[i][pt].split(' ')[0])
        if float(mov_entries[i][pt - 1].split(' ')[1]) == 0.0:
            sim_labels.append(LocLabels.IDLE)
            sim_events.append(Event(t[pt], 'start_h_action'))
        else:
            sim_labels.append(LocLabels.BUSY)
            sim_events.append(Event(t[pt], 'stop_h_action'))
        sig_pts = list(filter(lambda e: len(e.split(' ')) > 1 and
                                        prev <= float(e.split(' ')[0]) < curr, ftg_entries[i]))
        sig_pts = list(map(lambda x: SignalPoint(float(x.split(' ')[0]), 1, float(x.split(' ')[1])), sig_pts))
        sim_segm.append(sig_pts)
        prev = curr
    # last segment from last chg point to end of signal
    if float(mov_entries[i][- 2].split(' ')[1]) == 0.0:
        sim_labels.append(LocLabels.IDLE)
    else:
        sim_labels.append(LocLabels.BUSY)

    curr = float(ftg_entries[i][-2].split(' ')[0])
    sig_pts = list(filter(lambda e: len(e.split(' ')) > 1 and
                                    prev <= float(e.split(' ')[0]) < curr, ftg_entries[i]))
    sig_pts = list(map(lambda x: SignalPoint(float(x.split(' ')[0]), 1, float(x.split(' ')[1])), sig_pts))
    sim_segm.append(sig_pts)

    segments.append(sim_segm)
    labels.append(sim_labels)
    EVENTS.append(sim_events)

'''
ESTIMATE RATES FOR IDENTIFIED SEGMENTS
'''
est_rates = []
for sim in range(len(segments)):
    rates = []
    for segment in segments[sim]:
        t = [pt.timestamp for pt in segment]
        dts = [v - t[i - 1] for i, v in enumerate(t) if i > 0]
        avg_dt = sum(dts) / len(dts)
        x = [pt.value for pt in segment]
        try:
            dt = TimeInterval(segment[0].timestamp, segment[-1].timestamp)
            params, x_fore, fore = sig_mgr.n_predictions(segment, dt, 10, show_formula=False)
            est_rate = math.fabs(math.log(params[1])) / avg_dt * 2 if params[1] != 0.0 else 0.0
            # print('{:.5f} {}'.format(est_rate, labels[sim][segments[sim].index(segment)]))
            rates.append(est_rate)
        except ValueError:
            rates.append(None)
            print("Not enough data pts ({})".format(len(segment)))
    est_rates.append(rates)

'''
HYPOTHESIS TESTING on ESTIMATED RATES

const double YOUNG_SICK[2] = {0.004538, 0.003328}; 
const double YOUNG_SICK_SIGMA[2] = {0.000469, 0.001342};
'''

IDLE_DISTR = (0.003328, 0.001342)
BUSY_DISTR = (0.004538, 0.00065)

Z = 3
x_idle = np.linspace(IDLE_DISTR[0] - Z * IDLE_DISTR[1], IDLE_DISTR[0] + Z * IDLE_DISTR[1], 100)
idle_norm = stats.norm.pdf(x, IDLE_DISTR[0], IDLE_DISTR[1])
mus = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.IDLE]

x_busy = np.linspace(BUSY_DISTR[0] - Z * BUSY_DISTR[1], BUSY_DISTR[0] + Z * BUSY_DISTR[1], 100)
busy_norm = stats.norm.pdf(x, BUSY_DISTR[0], BUSY_DISTR[1])
lambdas = [rate for sim in est_rates for rate in sim if labels[est_rates.index(sim)][sim.index(rate)] == LocLabels.BUSY]

HT_outcome = []
for i in range(len(est_rates)):
    out = []
    for j in range(len(est_rates[i])):
        if labels[i][j] == LocLabels.IDLE:
            new = min(x_idle) <= est_rates[i][j] <= max(x_idle) if est_rates[i][j] is not None else None
        else:
            new = min(x_busy) <= est_rates[i][j] <= max(x_busy) if est_rates[i][j] is not None else None
        out.append(new)
    HT_outcome.append(out)

'''
REFINE GRAPH - STEP 0 check if a segment failed the test
'''

REFINEMENT_NEEDED = False

for i in range(len(HT_outcome)):
    for j in range(len(HT_outcome[i])):
        if not HT_outcome[i][j] and HT_outcome[i][j] is not None:
            REFINEMENT_NEEDED = True

'''
REFINE GRAPH - STEP 1 add locations
'''

# TODO: PROTOTYPE! should not only add a specific location
if REFINEMENT_NEEDED:
    LOC.append(Location('r_1', 'F = f_rest(t)'))
    HUMAN_FOLLOWER_HA.set_locations(LOC)
    ha_pltr.plot_ha(HUMAN_FOLLOWER_HA, 'human_follower_wip', view=True)

'''
REFINE GRAPH - STEP 2 identify ignored events
'''

if REFINEMENT_NEEDED:
    ign_events = []

    hPosX = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('internalHumX')]
    hPosX_entries = []
    for i in range(len(hPosX)):
        entries = hPosX[i].split('\n')
        entries = [entry for entry in entries if len(entry.split(' ')) > 1]
        hPosX_entries.append(entries)
        t = [float(entry.split(' ')[0]) for entry in entries]
        values = [float(entry.split(' ')[1]) for entry in entries]
        found_ignored = find_ignored(values)
        ign_events.append(found_ignored)
        # adds ignored events to sequence of prev. identified events
        for ign in found_ignored:
            prev = 0.0
            for j in range(len(EVENTS[i])):
                if prev <= t[ign] <= EVENTS[i][j].timestamp:
                    EVENTS[i].insert(j, Event(t[ign], IGNORED_EVENTS[0]))

for sim in EVENTS:
    print('TRACE {}:'.format(EVENTS.index(sim) + 1))
    [print(event) for event in sim]

'''
REFINE GRAPH - STEP 3 longest common suffix
'''
if REFINEMENT_NEEDED:
    path_lens = list(map(lambda i: len(i), EVENTS))
    shortest_path = [i for i in EVENTS if len(i) == min(path_lens)][0]
    LONG_COMM_SUFFIX = []
    for i in range(len(shortest_path)):
        curr_label = shortest_path[len(shortest_path) - 1 - i].label
        if all([sim[len(sim) - 1 - i].label == curr_label for sim in EVENTS]):
            LONG_COMM_SUFFIX.insert(0, curr_label)

    print('LONGEST COMMON SUFFIX')
    print(LONG_COMM_SUFFIX)

'''
REFINE GRAPH - STEP 4 ask for analyst confirmation
'''

# TODO: prototype, let's say they confirm
#  the correlation between event and new condition
CONFIRMATION = True

'''
REFINE GRAPH - STEP 5 fix edges
'''

if REFINEMENT_NEEDED and CONFIRMATION:
    new_guards: str = ''
    for event in LONG_COMM_SUFFIX:
        # TODO: prototype, should check if controllable
        if event not in IGNORED_EVENTS:
            involved_locations = []
            for edge in EDGES:
                if edge.sync.__contains__(event) and len(new_guards) > 0:
                    edge.set_guard('!' + new_guards)
                    involved_locations.append(edge.start)
            if event == LONG_COMM_SUFFIX[-1]:
                for loc in involved_locations:
                    EDGES.append(Edge(loc, LOC[-1], guard=new_guards, sync=event + '?'))
                    new_guards = ''
        else:
            new_guards += 'humInArea2'

    HUMAN_FOLLOWER_HA.set_edges(EDGES)

ha_pltr.plot_ha(HUMAN_FOLLOWER_HA, 'human_follower_final', view=True)

'''
PLOT TRACES WITH OVERLAY and HT outcome
'''

for i in range(len(segments)):
    plt.figure(figsize=(10, 5))
    for j in range(len(segments[i])):
        t = [pt.timestamp for pt in segments[i][j]]
        val = [pt.value for pt in segments[i][j]]
        color = 'black' if HT_outcome[i][j] or HT_outcome[i][j] is None else 'red'
        plt.plot(t, val, color=color)

    t = [float(x.split(' ')[0]) for x in mov_entries[i][1:len(mov_entries[i]) - 1] if len(x.split(' ')) > 1]
    mov_pts = [float(x.split(' ')[1]) for x in mov_entries[i][1:len(mov_entries[i]) - 1] if len(x.split(' ')) > 1]
    plt.plot(t, mov_pts, 'b--', linewidth=1)

    t = [float(x.split(' ')[0]) for x in idle_entries[i][1:len(idle_entries[i]) - 1] if len(x.split(' ')) > 1]
    idle_pts = [float(x.split(' ')[1]) for x in idle_entries[i][1:len(idle_entries[i]) - 1] if len(x.split(' ')) > 1]
    plt.plot(t, idle_pts, 'g--', linewidth=1)

    [plt.plot(t[n], 1, 'bx', markersize=12) for n in chg_pts[i]]
    if REFINEMENT_NEEDED:
        t = [float(x.split(' ')[0]) for x in hPosX_entries[i][1:len(hPosX_entries[i]) - 1] if len(x.split(' ')) > 1]
        [plt.plot(t[n], 1, 'rx', markersize=12) for n in ign_events[i]]
    plt.show()
