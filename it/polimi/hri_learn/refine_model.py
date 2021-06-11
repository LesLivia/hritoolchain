import math
import sys
import warnings
from typing import List

import pltr.ha_pltr as ha_pltr
from hri_learn.hl_star.learner import Learner
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher

# LEARNING PROCEDURE SETUP
warnings.filterwarnings('ignore')

CS_VERSION = sys.argv[2]
IDLE_DISTR = (0.003, 0.0001, 100)
BUSY_DISTR = (0.004, 0.0004, 100)

LOGGER = Logger()
PROB_DISTR = [IDLE_DISTR, BUSY_DISTR]

UNCONTR_EVTS = {}
if CS_VERSION == 'b':
    UNCONTR_EVTS = {'w': 'in_waiting_room'}  # , 'o': 'in_office'}
elif CS_VERSION == 'c':
    UNCONTR_EVTS = {'w': 'in_waiting_room', 'o': 'in_office'}
elif CS_VERSION == 'x':
    UNCONTR_EVTS = {'s': 'sat', 'r': 'ran', 'h': 'harsh_env', 'l': 'load', 'a': 'assisted_walk'}

CONTR_EVTS = {'u': 'start_moving', 'd': 'stop_moving'}


def idle_model(interval: List[float], F_0: float):
    return [F_0 * math.exp(-IDLE_DISTR[0] * (t - interval[0])) for t in interval]


def busy_model(interval: List[float], F_0: float):
    return [1 - (1 - F_0) * math.exp(-BUSY_DISTR[0] * (t - interval[0])) for t in interval]


MODELS = [idle_model, busy_model]

TEACHER = Teacher(MODELS, PROB_DISTR)
TEACHER.compute_symbols(list(UNCONTR_EVTS.keys()), list(CONTR_EVTS.keys()))
for sym in TEACHER.get_symbols().keys():
    print('{}: {}'.format(sym, TEACHER.get_symbols()[sym]))

LEARNER = Learner(TEACHER)

# RUN LEARNING ALGORITHM:
LEARNED_HA = LEARNER.run_hl_star(filter_empty=True)
ha_pltr.plot_ha(LEARNED_HA, 'H_{}_{}{}'.format(sys.argv[1], CS_VERSION, sys.argv[3]), view=True)
TEACHER.plot_distributions()

# s = Source(temp, filename="test.gv", format="pdf")
# s.view()
