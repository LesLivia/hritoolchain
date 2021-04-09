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

    def label_event(self, timestamp: float):
        fatigue = self.get_signals()[0]
        moving = self.get_signals()[2]

        identified_guard = ''

        curr_mov = list(filter(lambda x: x.timestamp == timestamp, moving))[0]
        identified_channel = self.get_channels()[0] if curr_mov.value == 1 else self.get_channels()[1]
        print(identified_channel)
