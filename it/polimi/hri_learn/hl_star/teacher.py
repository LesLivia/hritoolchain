from enum import Enum
from typing import List
from hri_learn.hl_star.evt_id import EventFactory
from domain.sigfeatures import SignalPoint


class Channels(Enum):
    START = 'u'
    STOP = 'd'


class Teacher:
    def __init__(self):
        self.symbols = None
        self.chg_pts = None
        self.events = None
        self.signals: List[List[SignalPoint]] = []
        self.evt_factory = EventFactory(None, None, None)

    def clear(self):
        self.events = None
        self.chg_pts = None
        self.signals: List[List[SignalPoint]] = []
        self.evt_factory.clear()

    '''
    SYMBOLS
    '''

    def set_symbols(self, symbols):
        self.symbols = symbols
        self.evt_factory.set_symbols(symbols)

    def get_symbols(self):
        return self.symbols

    def compute_symbols(self, guards: List[str], syncs: List[str]):
        symbols = {}
        self.evt_factory.set_guards(guards)
        self.evt_factory.set_channels(syncs)
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
        self.evt_factory.set_symbols(symbols)

    '''
    CHANGE POINTS
    '''

    def set_chg_pts(self, chg_pts: List[float]):
        self.chg_pts = chg_pts

    def get_chg_pts(self):
        return self.chg_pts

    def find_chg_pts(self, timestamps: List[float], values: List[float]):
        chg_pts: List[float] = []

        '''
        IDENTIFY CHANGE PTS IN DRIVER OVERLAY
        '''
        prev = values[0]
        for i in range(1, len(values)):
            curr = values[i]
            if curr != prev:
                chg_pts.append(timestamps[i])
            prev = curr

        self.set_chg_pts(chg_pts)

    '''
    SIGNALS
    '''

    def add_signal(self, signal: List[SignalPoint]):
        self.signals.append(signal)
        self.evt_factory.add_signal(signal)

    '''
    EVENTS
    '''

    def set_events(self, events):
        self.events = events

    def get_events(self):
        return self.events

    def identify_events(self):
        events = {}

        for pt in self.get_chg_pts():
            events[pt] = self.evt_factory.label_event(pt)

        self.set_events(events)
