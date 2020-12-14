from enum import Enum
from typing import List


class LocLabels(Enum):
    IDLE = 'idle'
    BUSY = 'busy'


class Location:
    def __init__(self, name: str):
        self.name = name


LOCATIONS: List[Location] = [Location(LocLabels.IDLE.value), Location(LocLabels.BUSY.value)]


class Edge:
    def __init__(self, start: Location, dest: Location, guard: str):
        self.start = start
        self.dest = dest
        self.guard = guard


class HybridAutomaton:
    def __init__(self, loc: List[Location], edges: List[Edge]):
        self.locations = loc
        self.edges = edges

    def set_locations(self, loc: List[Location]):
        self.locations = loc

    def set_edges(self, edges: List[Edge]):
        self.edges = edges
