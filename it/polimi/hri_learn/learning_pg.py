from typing import List
import os
import mgrs.ha_mgr as ha_mgr
import mgrs.sig_mgr as sig_mgr
import pltr.sig_pltr as sig_pltr
import pltr.ha_pltr as ha_pltr
from domain.hafeatures import HybridAutomaton, LOCATIONS, Edge
from domain.sigfeatures import SignalPoint, ChangePoint

LOG_PATH = "resources/sim_logs/sim{}"
FTG_LOG = 'humanFatigue.log'
POS_LOG = 'humanPosition.log'
HUM_ID = 1

SIM_ID = 1

while os.path.isdir(LOG_PATH.format(SIM_ID)):
    f = open(LOG_PATH.format(SIM_ID) + '/' + FTG_LOG, 'r')
    lines = f.readlines()
    lines = list(filter(lambda l: len(l) > 2, lines))
    lines = list(filter(lambda l: l.split(':')[1] == 'hum' + str(HUM_ID), lines))

    entries: List[SignalPoint] = []
    for line in lines:
        fields = line.split(':')
        entries.append(SignalPoint(float(fields[0]), int(fields[1].replace('hum', '')), float(fields[2])))

    change_pts: List[ChangePoint] = sig_mgr.identify_change_pts(entries)

    # for entry in entries:
    #     print(entry)
    #     change_pt = list(filter(lambda pt: pt.dt.t_min == entry.timestamp, change_pts))
    #     if len(change_pt) > 0:
    #         print(change_pt[0])

    sig_pltr.plot_sig(entries, change_pts)

    HUM_HA: HybridAutomaton = HybridAutomaton(LOCATIONS, [])
    edges: List[Edge] = ha_mgr.identify_edges(change_pts)
    HUM_HA.set_edges(edges)

    ha_pltr.plot_ha(HUM_HA, 'ha_{}'.format(SIM_ID))
    SIM_ID += 1
