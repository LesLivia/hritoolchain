from enum import Enum
from typing import List


class LocLabels(Enum):
    IDLE = 'idle'
    BUSY = 'busy'


class Location:
    def __init__(self, name: str, flow_cond: str):
        self.name = name
        self.flow_cond = flow_cond

    def set_flow_cond(self, flow_cond: str):
        self.flow_cond = flow_cond


LOCATIONS: List[Location] = [Location(LocLabels.IDLE.value, None), Location(LocLabels.BUSY.value, None)]


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
