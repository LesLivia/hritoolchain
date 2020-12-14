from typing import List

from domain.hafeatures import SignalPoint, ChangePoint

import mgrs.sig_mgr as sig_mgr
import pltr.sig_pltr as sig_pltr

LOG_PATH = "resources/sim_logs/humanFatigue.log"
HUM_ID = 1

f = open(LOG_PATH, 'r')
lines = f.readlines()
lines = list(filter(lambda l: len(l) > 2, lines))
lines = list(filter(lambda l: l.split('#')[1] == 'hum' + str(HUM_ID), lines))

entries: List[SignalPoint] = []
for line in lines:
    fields = line.split('#')
    entries.append(SignalPoint(float(fields[0]), int(fields[1].replace('hum', '')), float(fields[2])))

change_pts: List[ChangePoint] = sig_mgr.identify_change_pts(entries)

for entry in entries:
    print(entry)
    change_pt = list(filter(lambda pt: pt.dt.t_min == entry.timestamp, change_pts))
    if len(change_pt) > 0:
        print(change_pt[0])

sig_pltr.plot_sig(entries, change_pts)
