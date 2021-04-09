import warnings
from typing import List


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

'''
SETUP LEARNING PROCEDURE
'''
warnings.filterwarnings('ignore')

LOG_PATH = 'resources/uppaal_logs/test.txt'

'''
ACQUIRE TRACES
'''
f = open(LOG_PATH)
lines = f.read()
variables = lines.split('#')

ftg = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.F')]
hMov = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.busy')]
hIdle = [variables[i] for i in range(len(variables)) if variables[i - 1].__contains__('amy.idle')]

print("HL* (INFO)\tTRACES TO ANALYZE: {}".format(len(ftg)))

# while there is a trace to parse
for trace in range(len(ftg)):
    '''
    PARSE TRACES
    '''
    entries = ftg[trace].split('\n')[1:]
    ftg_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]

    entries = hMov[trace].split('\n')[1:]
    mov_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]

    entries = hIdle[trace].split('\n')[1:]
    idle_entries = [entry for (i, entry) in enumerate(entries) if i == 0 or entries[i - 1] != entry]

    chg_pts = find_chg_pts([float(x.split(' ')[1]) for x in mov_entries if len(x.split(' ')) > 1])
    print(chg_pts)
    # run hl*
