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
if CS_VERSION == 'a':
    LOG_PATH = 'resources/uppaal_logs/test.txt'
    UNCONTR_EVTS = {'e': 'enter_area_2'}  # , 'r': 'is_running', 'o': 'enter_office'}
    IDLE_DISTR = (0.003328, 0.001342)
    BUSY_DISTR = (0.004538, 0.00065)
elif CS_VERSION == 'b':
    LOG_PATH = 'resources/uppaal_logs/test2.txt'
    UNCONTR_EVTS = {'e': 'enter_area_2'}  # , 'r': 'is_running', 'o': 'enter_office'}
    IDLE_DISTR = (0.003328, 0.001342)
    BUSY_DISTR = (0.004538, 0.00065)
else:
    LOG_PATH = 'resources/uppaal_logs/cons.txt'
    UNCONTR_EVTS = {'e': 'enter_area_2', 'o': 'enter_office'}  # , 'r': 'is_running',
    IDLE_DISTR = (0.003328, 0.001342)
    BUSY_DISTR = (0.004538, 0.00650)
    SWITCH_TIME = 94.1

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

# TRACE ACQUISIION
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hPosX = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('internalHumX')]
if CS_VERSION == 'c':
    hPosY = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('internalHumY')]
    ftg_bis = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy_bis.F')]
    hMov_bis = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy_bis.busy')]

LOGGER.info("TRACES TO ANALYZE-> {}\n".format(len(ftg)))

for trace in range(len(ftg)):
    LOGGER.msg("ANALYZING TRACE {}:\n".format(trace + 1))
    TEACHER.clear()

    # TRACE PARSING
    entries = ftg[trace].split('\n')[1:]

    ftg_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in ftg_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in ftg_entries if len(x.split(' ')) > 1]
    if CS_VERSION == 'c' and trace == 0:
        values = [v for (i, v) in enumerate(values) if timestamps[i] < SWITCH_TIME]
        timestamps = [t for t in timestamps if t < SWITCH_TIME]
        entries_bis = ftg_bis[trace].split('\n')[1:]
        ftg_bis_entries = [entry for (i, entry) in enumerate(entries_bis) if i == 0 or entries_bis[i - 1] != entry]
        timestamps_bis = [float(x.split(' ')[0]) for x in ftg_bis_entries if len(x.split(' ')) > 1]
        values_bis = [float(x.split(' ')[1]) for x in ftg_bis_entries if len(x.split(' ')) > 1]
        values_bis = [v for (i, v) in enumerate(values_bis) if timestamps_bis[i] >= SWITCH_TIME]
        timestamps_bis = [t for t in timestamps_bis if t >= SWITCH_TIME]
        timestamps = timestamps + timestamps_bis
        values = values + values_bis
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    entries = hPosX[trace].split('\n')[1:]
    posX_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in posX_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in posX_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    entries = hMov[trace].split('\n')[1:]
    mov_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]  # DRIVER OVERLAY
    driver_timestamps = [float(x.split(' ')[0]) for x in mov_entries if len(x.split(' ')) > 1]
    driver_values = [float(x.split(' ')[1]) for x in mov_entries if len(x.split(' ')) > 1]
    if CS_VERSION == 'c' and trace == 0:
        driver_values = [v for (i, v) in enumerate(driver_values) if driver_timestamps[i] < SWITCH_TIME]
        driver_timestamps = [t for t in driver_timestamps if t < SWITCH_TIME]
        entries_bis = hMov_bis[trace].split('\n')[1:]
        hMov_bis_entries = [entry for (i, entry) in enumerate(entries_bis) if i == 0 or entries_bis[i - 1] != entry]
        timestamps_bis = [float(x.split(' ')[0]) for x in hMov_bis_entries if len(x.split(' ')) > 1]
        values_bis = [float(x.split(' ')[1]) for x in hMov_bis_entries if len(x.split(' ')) > 1]
        values_bis = [v for (i, v) in enumerate(values_bis) if timestamps_bis[i] >= SWITCH_TIME]
        timestamps_bis = [t for t in timestamps_bis if t >= SWITCH_TIME]
        driver_timestamps = driver_timestamps + timestamps_bis
        driver_values = driver_values + values_bis
    TEACHER.add_signal([SignalPoint(driver_timestamps[i], 1, driver_values[i]) for i in range(len(driver_timestamps))],
                       trace)

    if CS_VERSION == 'c':
        entries = hPosY[trace].split('\n')[1:]
        posY_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
        timestamps = [float(x.split(' ')[0]) for x in posY_entries if len(x.split(' ')) > 1]
        values = [float(x.split(' ')[1]) for x in posY_entries if len(x.split(' ')) > 1]
        TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))], trace)

    # IDENTIFY EVENTS:
    # (Updates Teacher's knowledge of system behavior)
    TEACHER.find_chg_pts(driver_timestamps, driver_values)
    TEACHER.identify_events(trace)
    TEACHER.plot_trace(trace, 'TRACE {}'.format(trace + 1), 't [s]', 'F [%]')

# RUN LEARNING ALGORITHM:
LEARNED_HA = LEARNER.run_hl_star(filter_empty=True)
ha_pltr.plot_ha(LEARNED_HA, 'H_{}_{}'.format(sys.argv[1], CS_VERSION), view=True)
