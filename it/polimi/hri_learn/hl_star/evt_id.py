from domain.sigfeatures import SignalPoint
from typing import List


class EventFactory:
    def __init__(self, guards, channels, symbols):
        self.guards = guards
        self.channels = channels
        self.symbols = symbols
        self.signals: List[List[SignalPoint]] = []

    def clear(self):
        self.signals: List[List[SignalPoint]] = []

    def set_guards(self, guards):
        self.guards = guards

    def set_channels(self, channels):
        self.channels = channels

    def set_symbols(self, symbols):
        self.symbols = symbols

    def add_signal(self, signal):
        self.signals.append(signal)

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
            This method must be RE-IMPLEMENTED for each new case study:
            each guard corresponds to a specific condition on a signal,
            the same stands for channels.
    '''

    def label_event(self, timestamp: float):
        posX = self.get_signals()[1]
        moving = self.get_signals()[2]

        identified_guard = ''
        '''
        Repeat for every guard in the system
        '''
        curr_posx = list(filter(lambda x: x.timestamp <= timestamp, posX))[-1]
        identified_guard += self.get_guards()[0] if curr_posx.value >= 4000.0 else '!' + self.get_guards()[0]

        '''
        Repeat for every channel in the system
        '''
        curr_mov = list(filter(lambda x: x.timestamp == timestamp, moving))[0]
        identified_channel = self.get_channels()[0] if curr_mov.value == 1 else self.get_channels()[1]

        '''
        Find symbol associated with guard-channel combination
        '''
        combination = identified_guard + ' and ' + identified_channel
        for key in self.get_symbols().keys():
            if self.get_symbols()[key] == combination:
                return key
