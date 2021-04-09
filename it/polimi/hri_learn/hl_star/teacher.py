from enum import Enum
from typing import List


class Channels(Enum):
    START = 'u'
    STOP = 'd'


class Teacher:
    def __init__(self):
        pass

    def set_symbols(self, symbols):
        self.symbols = symbols

    def compute_symbols(self, guards: List[str], syncs: List[str]):
        symbols = {}
        '''
        Compute all permutations of guards
        '''
        guards_comb = [''] * 2 ** len(guards)
        for (i, g) in enumerate(guards):
            pref = ''
            for j in range(2 ** len(guards)):
                guards_comb[j] += pref + g
                if (j + 1) % ((2 ** len(guards)) / (2 ** (i + 1))) == 0:
                    pref = '!' if pref == '' else ''
        '''
        Combine all guards with channels
        '''
        for chn in syncs:
            for (index, g) in enumerate(guards_comb):
                symbols[chn + '_' + str(index + 1)] = g + ' and ' + chn

        self.set_symbols(symbols)

    def find_chg_pts(self, values: List[float]):
        chg_pts: List[int] = []
        prev = values[0]
        for i in range(1, len(values)):
            curr = values[i]
            if curr != prev:
                chg_pts.append(i)
            prev = curr
        return chg_pts
