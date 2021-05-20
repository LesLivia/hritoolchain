import math
import sys
import warnings
from typing import List

import pltr.ha_pltr as ha_pltr
from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.learner import Learner
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher

# LEARNING PROCEDURE SETUP
warnings.filterwarnings('ignore')

CS_VERSION = sys.argv[2]
UNCONTR_EVTS = {}  # 'e': 'in_waiting_room' , 'r': 'is_running', 'o': 'enter_office'}
IDLE_DISTR = (0.003328, 0.001342, 100)
BUSY_DISTR = (0.004538, 0.000469, 100)

LOGGER = Logger()

CONTR_EVTS = {'u': 'start_moving', 'd': 'stop_moving'}
PROB_DISTR = [IDLE_DISTR, BUSY_DISTR]


def idle_model(interval: List[float], F_0: float):
    return [F_0 * math.exp(-IDLE_DISTR[0] * (t - interval[0])) for t in interval]


def busy_model(interval: List[float], F_0: float):
    return [1 - (1 - F_0) * math.exp(-BUSY_DISTR[0] * (t - interval[0])) for t in interval]


MODELS = [idle_model, busy_model]

TEACHER = Teacher(MODELS, PROB_DISTR)
TEACHER.compute_symbols(list(UNCONTR_EVTS.keys()), list(CONTR_EVTS.keys()))
print(TEACHER.get_symbols())

LEARNER = Learner(TEACHER)

# RUN LEARNING ALGORITHM:
LEARNED_HA = LEARNER.run_hl_star(filter_empty=True)
ha_pltr.plot_ha(LEARNED_HA, 'H_{}_{}'.format(sys.argv[1], CS_VERSION), view=True)
TEACHER.plot_distributions()
