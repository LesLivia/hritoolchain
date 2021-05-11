import subprocess
from typing import List
import random
import sys
import os
from hl_star.logger import Logger

UPP_MODEL_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/thermostat.xml'
UPP_QUERY_PATH = '/Users/lestingi/Desktop/phd-workspace/hri-models/uppaal-models/thermostat.q'
UPP_EXE_PATH = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin'
UPP_OUT_PATH = '/Users/lestingi/PycharmProjects/hritoolchain/resources/uppaal_logs/rt_traces/{}.txt'
SCRIPT_PATH = '/Users/lestingi/PycharmProjects/hritoolchain/resources/scripts/verify.sh'
MAX_E = 15

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
        m_r = open(UPP_MODEL_PATH, 'r')

        new_line_1 = 'bool force_exe = true;\n'
        values = self.get_evt_str()
        new_line_2 = 'int force_open[MAX_E] = ' + values

        lines = m_r.readlines()
        found = False
        for line in lines:
            if line.startswith('bool force_exe') and not found:
                lines[lines.index(line)] = new_line_1
                found = True
            elif line.startswith('int force_open'):
                lines[lines.index(line)] = new_line_2
                break

        m_r.close()
        m_w = open(UPP_MODEL_PATH, 'w')
        m_w.writelines(lines)
        m_w.close()

    def get_traces(self):
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
            return UPP_OUT_PATH.format(s)
        else:
            return None
