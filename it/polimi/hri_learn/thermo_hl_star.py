import math
import sys
import warnings
from typing import List

import pltr.ha_pltr as ha_pltr
from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.learner import Learner
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher

'''
SETUP LEARNING PROCEDURE
'''
warnings.filterwarnings('ignore')

CS_VERSION = sys.argv[2]

CONTR_EVTS = {'h': 'turn_on_heat', 'c': 'turn_off_heat'}
CLOSED_R = 100.0
OFF_DISTR = (100.0, 1.0, 200)
ON_DISTR = (0.7, 0.01, 200)


def off_model(interval: List[float], T_0: float):
    return [T_0 * math.exp(-1 / OFF_DISTR[0] * (t - interval[0])) for t in interval]


def on_model(interval: List[float], T_0: float):
    coeff = CLOSED_R * ON_DISTR[0]
    return [coeff - (coeff - T_0) * math.exp(-(1 / CLOSED_R) * (t - interval[0])) for t in interval]


def off_model_2(interval: List[float], T_0: float):
    return [T_0 - 1 / OFF_DISTR[0] * (t - interval[0]) for t in interval]


def on_model_2(interval: List[float], T_0: float):
    return [T_0 + ON_DISTR[0] * (t - interval[0]) for t in interval]


LOG_PATH = 'resources/uppaal_logs/thermo_{}.txt'.format(sys.argv[3])
if CS_VERSION == 'a':
    UNCONTR_EVTS = {'o': 'one_window_open'}
    MODELS = [off_model, on_model]
    PROB_DISTR = [OFF_DISTR, ON_DISTR]
elif CS_VERSION == 'b':
    UNCONTR_EVTS = {'o': 'one_window_open', 't': 'two_windows_open'}
    MODELS = [off_model, on_model]
    PROB_DISTR = [OFF_DISTR, ON_DISTR]
elif CS_VERSION == 'c':
    UNCONTR_EVTS = {'o': 'one_window_open', 't': 'two_windows_open'}
    MODELS = [off_model, on_model, on_model_2]
    PROB_DISTR = [OFF_DISTR, ON_DISTR]

LOGGER = Logger()

TEACHER = Teacher(MODELS, PROB_DISTR)
TEACHER.compute_symbols(list(UNCONTR_EVTS.keys()), list(CONTR_EVTS.keys()))
print(TEACHER.get_symbols())

LEARNER = Learner(TEACHER)

'''
ACQUIRE TRACES
'''
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

temp = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('T_r')]
hOn = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('t.ON')]
wOpen = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('r.open')]

LOGGER.info("TRACES TO ANALYZE-> {}\n".format(len(temp)))

for trace in range(len(temp)):
    LOGGER.info("ANALYZING TRACE {}...\n".format(trace + 1))
    TEACHER.clear()

    '''
    PARSE TRACES
    '''
    entries = hOn[trace].split('\n')[1:]
    hOn_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]  # DRIVER OVERLAY
    timestamps = [float(x.split(' ')[0]) for x in hOn_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in hOn_entries if len(x.split(' ')) > 1]
    driver_t = timestamps
    driver_v = values
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    entries = temp[trace].split('\n')[1:]
    temp_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in temp_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in temp_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    entries = wOpen[trace].split('\n')[1:]
    wOpen_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in wOpen_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in wOpen_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    # IDENTIFY EVENTS:
    # (Updates Teacher's knowledge of system behavior)
    TEACHER.find_chg_pts(driver_t, driver_v)
    TEACHER.identify_events(trace)
    # TEACHER.plot_trace(trace, 'TRACE {}'.format(trace + 1), 't [min]', 'T [°C]')

# RUN LEARNING ALGORITHM:
LEARNED_HA = LEARNER.run_hl_star(filter_empty=True)
ha_pltr.plot_ha(LEARNED_HA, 'H_{}_{}{}'.format(sys.argv[1], CS_VERSION, sys.argv[3]), view=True)
TEACHER.plot_distributions()
