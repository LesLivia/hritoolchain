import warnings
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher
from domain.sigfeatures import SignalPoint

'''
SETUP LEARNING PROCEDURE
'''
warnings.filterwarnings('ignore')

LOG_PATH = 'resources/uppaal_logs/test.txt'
LOGGER = Logger()

UNCONTR_EVTS = {'e': 'enter_area_2'}  # , 'r': 'is_running', 'o': 'enter_office'}
CONTR_EVTS = {'u': 'start_moving', 'd': 'stop_moving'}

TEACHER = Teacher()
TEACHER.compute_symbols(list(UNCONTR_EVTS.keys()), list(CONTR_EVTS.keys()))

'''
ACQUIRE TRACES
'''
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hIdle = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.idle')]

LOGGER.info("TRACES TO ANALYZE: {}".format(len(ftg)))

for trace in range(len(ftg)):
    LOGGER.info("ANALYZING TRACE: {}".format(trace + 1))
    TEACHER.clear()

    '''
    PARSE TRACES
    '''
    entries = ftg[trace].split('\n')[1:]
    ftg_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in ftg_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in ftg_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    entries = hIdle[trace].split('\n')[1:]
    idle_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]
    timestamps = [float(x.split(' ')[0]) for x in idle_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in idle_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    entries = hMov[trace].split('\n')[1:]
    mov_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]  # DRIVER OVERLAY
    timestamps = [float(x.split(' ')[0]) for x in mov_entries if len(x.split(' ')) > 1]
    values = [float(x.split(' ')[1]) for x in mov_entries if len(x.split(' ')) > 1]
    TEACHER.add_signal([SignalPoint(timestamps[i], 1, values[i]) for i in range(len(timestamps))])

    # IDENTIFY EVENTS
    TEACHER.find_chg_pts(timestamps, values)
    TEACHER.identify_events()

    # run hl_star
