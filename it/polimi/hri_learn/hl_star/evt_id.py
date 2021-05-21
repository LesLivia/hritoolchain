import math
import sys
from typing import List

from domain.sigfeatures import SignalPoint
from hl_star.logger import Logger

'''
WARNING! 
        These constants may change if the system changes:
        default model and distr. for empty string.
'''
LOGGER = Logger()
CASE_STUDY = sys.argv[1]
CS_VERSION = sys.argv[2]
MAIN_SIGNAL = None
if CASE_STUDY == 'hri':
    MAIN_SIGNAL = 0
    DRIVER_SIG = 2
    DEFAULT_MODEL = 0
    DEFAULT_DISTR = 0
    MODEL_TO_DISTR_MAP = {0: 0, 1: 1}  # <- HRI
else:
    ON_R = 100.0
    MAIN_SIGNAL = 1
    DRIVER_SIG = 0
    if CS_VERSION == 'a' or CS_VERSION == 'b':
        MODEL_TO_DISTR_MAP = {0: 0, 1: 1}  # <- THERMOSTAT
        DEFAULT_MODEL = 0
        DEFAULT_DISTR = 0
    else:
        MODEL_TO_DISTR_MAP = {0: 0, 1: 2}
        DEFAULT_MODEL = 0
        DEFAULT_DISTR = 0


class EventFactory:
    def __init__(self, guards, channels, symbols):
        self.guards = guards
        self.channels = channels
        self.symbols = symbols
        self.signals: List[List[List[SignalPoint]]] = []

    def clear(self):
        self.signals.append([])

    def set_guards(self, guards):
        self.guards = guards

    def set_channels(self, channels):
        self.channels = channels

    def set_symbols(self, symbols):
        self.symbols = symbols

    def add_signal(self, signal, trace):
        self.signals[trace].append(signal)

    def get_guards(self):
        return self.guards

    def get_channels(self):
        return self.channels

    def get_symbols(self):
        return self.symbols

    def get_signals(self):
        return self.signals

    '''
    WARNING! 
            This method must be RE-IMPLEMENTED for each system:
            each guard corresponds to a specific condition on a signal,
            the same stands for channels.
    '''

    def label_event(self, timestamp: float, trace):
        if CASE_STUDY == 'hri':
            posX = self.get_signals()[trace][1]
            moving = self.get_signals()[trace][2]

            identified_guard = ''
            '''
            Repeat for every guard in the system
            '''
            if CS_VERSION in ['b', 'c']:
                curr_posx = list(filter(lambda x: x.timestamp <= timestamp, posX))[-1]
                identified_guard += self.get_guards()[0] if 2000.0 <= curr_posx.value <= 3000.0 else '!' + \
                                                                                                     self.get_guards()[
                                                                                                         0]
            if CS_VERSION in ['c']:
                posY = self.get_signals()[trace][3]
                curr_posx = list(filter(lambda x: x.timestamp <= timestamp, posX))[-1]
                curr_posy = list(filter(lambda x: x.timestamp <= timestamp, posY))[-1]
                in_office = curr_posx.value < 2000.0 and 1000.0 <= curr_posy.value <= 3000.0
                identified_guard += self.get_guards()[1] if in_office else '!' + self.get_guards()[1]

            '''
            Repeat for every channel in the system
            '''
            curr_mov = list(filter(lambda x: x.timestamp == timestamp, moving))[0]
            identified_channel = self.get_channels()[0] if curr_mov.value == 1 else self.get_channels()[1]
        else:
            wOpen = self.get_signals()[trace][2]
            heatOn = self.get_signals()[trace][0]

            identified_guard = ''
            '''
            Repeat for every guard in the system
            '''
            curr_wOpen = list(filter(lambda x: x.timestamp <= timestamp, wOpen))[-1]
            identified_guard += self.get_guards()[0] if curr_wOpen.value == 1.0 else '!' + self.get_guards()[0]
            if CS_VERSION == 'b' or CS_VERSION == 'c':
                identified_guard += self.get_guards()[1] if curr_wOpen.value == 2.0 else '!' + self.get_guards()[1]
                # identified_guard += self.get_guards()[2] if curr_wOpen.value == 0.0 else '!' + self.get_guards()[2]

            '''
            Repeat for every channel in the system
            '''
            curr_heatOn = list(filter(lambda x: x.timestamp == timestamp, heatOn))[0]
            identified_channel = self.get_channels()[0] if curr_heatOn.value == 1.0 else self.get_channels()[1]

        '''
        Find symbol associated with guard-channel combination
        '''
        combination = identified_guard + ' and ' + identified_channel
        for key in self.get_symbols().keys():
            if self.get_symbols()[key] == combination:
                return key

    '''
    WARNING! 
            This method must be RE-IMPLEMENTED for each system:
            returns metric for HT queries.
    '''

    def get_ht_metric(self, segment: List[SignalPoint], model=None):
        if CASE_STUDY == 'hri':
            return self.get_ftg_metric(segment, model)
        else:
            return self.get_thermo_metric(segment, model)

    def get_ftg_metric(self, segment: List[SignalPoint], model: int):
        try:
            val = [pt.value for pt in segment]
            # metric for walking
            if model == 1:
                lambdas = []
                for (i, v) in enumerate(val):
                    if i > 0 and v != val[i - 1]:
                        lambdas.append(math.log((1 - v) / (1 - val[i - 1])))
                est_rate = sum(lambdas) / len(lambdas) if len(lambdas) > 0 else None
            # metric for standing/sitting
            else:
                mus = []
                for (i, v) in enumerate(val):
                    if i > 0 and v != val[i - 1] and val[i - 1] != 0:
                        mus.append(math.log(v / val[i - 1]))
                est_rate = sum(mus) / len(mus) if len(mus) > 0 else None

            return abs(est_rate) if est_rate is not None else None
        except ValueError:
            return None

    def get_thermo_metric(self, segment: List[SignalPoint], model: int):
        try:
            val = [pt.value for pt in segment]
            if model in [1, 2]:
                if CS_VERSION != 'c' or (CS_VERSION == 'c' and model == 1):
                    increments = []
                    for (i, pt) in enumerate(val):
                        if i > 0 and pt != val[i - 1]:
                            increments.append(pt - val[i - 1] * math.exp(-1 / ON_R))
                    Ks = [delta_t / (ON_R * (1 - math.exp(-1 / ON_R))) for delta_t in increments if delta_t != 0]

                    LOGGER.info('Estimating rate with heat on ({})'.format(model))
                    est_rate = sum(Ks) / len(Ks) if len(Ks) > 0 else None
                else:
                    increments = []
                    for (i, pt) in enumerate(val):
                        if i > 0:
                            increments.append(pt - val[i - 1])
                    increments = [i for i in increments if i != 0]
                    LOGGER.info('Estimating rate with heat on ({})'.format(model))
                    est_rate = sum(increments) / len(increments) if len(increments) > 0 else None
            else:
                increments = []
                for (i, pt) in enumerate(val):
                    if i > 0:
                        increments.append(pt / val[i - 1])

                Rs = [-1 / math.log(delta_t) for delta_t in increments if delta_t != 1]

                LOGGER.info('Estimating rate with heat off ({})'.format(model))
                est_rate = sum(Rs) / len(Rs) if len(Rs) > 0 else None

            return est_rate
        except ValueError:
            return None
