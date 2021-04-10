import warnings
import math
from typing import List
from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.learner import Learner
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher

'''
SETUP LEARNING PROCEDURE
'''
warnings.filterwarnings('ignore')

LOG_PATH = 'resources/uppaal_logs/test.txt'
LOGGER = Logger()

UNCONTR_EVTS = {'e': 'enter_area_2'}  # , 'r': 'is_running', 'o': 'enter_office'}
CONTR_EVTS = {'u': 'start_moving', 'd': 'stop_moving'}
IDLE_DISTR = [(0.003328, 0.001342)]
BUSY_DISTR = [(0.004538, 0.00065)]
PROB_DISTR = [IDLE_DISTR, BUSY_DISTR]


def idle_model(interval: List[float], F_0: float):
    return [F_0 * math.exp(-IDLE_DISTR[0][0] * (t - interval[0])) for t in interval]


def busy_model(interval: List[float], F_0: float):
    return [1 - (1 - F_0) * math.exp(-BUSY_DISTR[0][0] * (t - interval[0])) for t in interval]


MODELS = [idle_model, busy_model]

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

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hIdle = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.idle')]
hPosX = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('internalHumX')]

LOGGER.info("TRACES TO ANALYZE-> {}".format(len(ftg)))

for trace in range(len(ftg)):
    LOGGER.info("ANALYZING TRACE {}".format(trace + 1))
    TEACHER.clear()

    '''
    PARSE TRACES
    '''
    entries = ftg[trace].split('\n')[1:]
    ftg_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in ftg_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in ftg_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    entries = hPosX[trace].split('\n')[1:]
    posX_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in posX_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in posX_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    entries = hMov[trace].split('\n')[1:]
    mov_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]  # DRIVER OVERLAY
    timestamps = [float(x.split(' ')[0]) for x in mov_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in mov_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    # IDENTIFY EVENTS:
    # (Updates Teacher's knowledge of system behavior)
    TEACHER.find_chg_pts(timestamps, values)
    TEACHER.identify_events()
    TEACHER.plot_trace('TRACE {}'.format(trace + 1), 't [s]', 'F [%]')

    # RUN LEARNING ALGORITHM:
    LEARNER.run_hl_star()
