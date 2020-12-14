from typing import List
from enum import Enum


class SignalPoint:
    def __init__(self, t: float, humId: int, val: float):
        self.timestamp = t
        self.humId = humId
        self.value = val
        self.notes: List[str] = []

    def __str__(self):
        return '(hum {}) {}: {}'.format(self.humId, self.timestamp, self.value)


class TimeInterval:
    def __init__(self, t_min: float, t_max: float):
        self.t_min = t_min
        self.t_max = t_max


class Labels(Enum):
    STARTED = 'walk'
    STOPPED = 'stop'


class ChangePoint:
    def __init__(self, t: TimeInterval, label: Labels):
        self.dt = t
        self.event = label

    def __str__(self):
        return '({}, {}) -> {}'.format(self.dt.t_min, self.dt.t_max, self.event)
