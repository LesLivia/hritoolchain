import subprocess
from typing import List
import random
import sys
import os
from hl_star.logger import Logger

CS = sys.argv[1]
UPP_EXE_PATH = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin'
UPP_OUT_PATH = '/Users/lestingi/PycharmProjects/hritoolchain/resources/uppaal_logs/rt_traces/{}.txt'
SCRIPT_PATH = '/Users/lestingi/PycharmProjects/hritoolchain/resources/scripts/verify.sh'

# FIXME: should be relative paths, or passed as input args
if CS == 'hri':
    LINE_1 = ['bool force_exe = true;\n', 'bool force_exe']
    LINE_2 = ['int force_act[MAX_E] = ', 'int force_act']
    LINE_3 = ['const int TAU = {};\n', 'const int TAU']
    LINE_4 = ['r = Room_{}(15.2);\n', 'r = Room']
    UPP_MODEL_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/hri-w_ref.xml'
    UPP_QUERY_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/hri-w_ref.q'
else:
    LINE_1 = ['bool force_exe = true;\n', 'bool force_exe']
    LINE_2 = ['int force_open[MAX_E] = ', 'int force_open']
    LINE_3 = ['const int TAU = {};\n', 'const int TAU']
    LINE_4 = ['r = Room_{}(15.2);\n', 'r = Room']
    UPP_MODEL_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/thermostat.xml'
    UPP_QUERY_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/thermostat.q'

MAX_E = 15
CS_VERSION = int(sys.argv[3])

LOGGER = Logger()


class TraceGenerator:
    def __init__(self, word: str = None):
        self.word = word
        self.events: List[str] = []
        self.evt_int: List[int] = []

    def set_word(self, w: str):
        self.events = []
        self.evt_int = []
        self.word = w

    def split_word(self):
        for i in range(0, len(self.word) - 2, 3):
            self.events.append(self.word[i:i + 3])

    def evts_to_ints(self):
        for evt in self.events:
            if CS == 'hri':
                if evt in ['u_1']:
                    self.evt_int.append(1)
                else:
                    self.evt_int.append(0)
            else:
                # for thermo example: associates a specific value
                # to variable open for each event in the requested trace
                if CS_VERSION < 8:
                    if evt in ['h_1', 'c_1']:
                        self.evt_int.append(1)
                    elif evt in ['h_2', 'c_2']:
                        self.evt_int.append(0)
                else:
                    if evt in ['h_1', 'c_1']:
                        self.evt_int.append(-1)
                    elif evt in ['h_2', 'c_2']:
                        self.evt_int.append(1)
                    elif evt in ['h_3', 'c_3']:
                        self.evt_int.append(2)
                    elif evt in ['h_4', 'c_4']:
                        self.evt_int.append(0)

    def get_evt_str(self):
        self.split_word()
        self.evts_to_ints()

        res = '{'
        i = 0
        for evt in self.evt_int:
            res += str(evt) + ', '
            i += 1
        while i < MAX_E - 1:
            res += '-1, '
            i += 1
        res += '-1};\n'
        return res

    def fix_model(self):
        # customized uppaal model based on requested trace
        m_r = open(UPP_MODEL_PATH, 'r')

        new_line_1 = LINE_1[0]
        values = self.get_evt_str()
        new_line_2 = LINE_2[0] + values
        tau = max(len(self.evt_int) * 70, 200)
        new_line_3 = LINE_3[0].format(tau)
        new_line_4 = LINE_4[0].format(CS_VERSION)

        lines = m_r.readlines()
        found = [False, False, False]
        for line in lines:
            if line.startswith(LINE_1[1]) and not found[0]:
                lines[lines.index(line)] = new_line_1
                found[0] = True
            elif line.startswith(LINE_2[1]) and not found[1]:
                lines[lines.index(line)] = new_line_2
                found[1] = True
            elif line.startswith(LINE_3[1]) and not found[2]:
                lines[lines.index(line)] = new_line_3
                found[2] = True
            elif line.startswith(LINE_4[1]):
                lines[lines.index(line)] = new_line_4
                break

        m_r.close()
        m_w = open(UPP_MODEL_PATH, 'w')
        m_w.writelines(lines)
        m_w.close()

    def get_traces(self):
        # sample new traces through uppaal command line tool
        self.fix_model()
        random.seed()
        n = random.randint(0, 2 ** 32)
        case_study = sys.argv[1]
        version = sys.argv[2]
        s = '{}_{}_{}'.format(case_study, version, n)
        FNULL = open(os.devnull, 'w')
        LOGGER.debug('!! GENERATING NEW TRACES FOR: {} !!'.format(self.word))
        p = subprocess.Popen([SCRIPT_PATH, UPP_EXE_PATH, UPP_MODEL_PATH, UPP_QUERY_PATH, UPP_OUT_PATH.format(s)],
                             stdout=FNULL)
        p.wait()
        if p.returncode == 0:
            LOGGER.info('TRACES SAVED TO ' + s)
            # returns out file where new traces are stored
            return UPP_OUT_PATH.format(s)
        else:
            return None
