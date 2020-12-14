from typing import List
from graphviz import Digraph


class Entry:
    def __init__(self, t: int, humId: int, val: float):
        self.timestamp = t
        self.humId = humId
        self.value = val
        self.notes: List[str] = []



    def print(self):
        print('(hum {}) {}: {}'.format(self.humId, self.timestamp, self.value))


LOG_PATH = "resources/sim_logs/humanFatigue.log"
HUM_ID = 1

f = open(LOG_PATH, 'r')
lines = f.readlines()
lines = list(filter(lambda l: len(l) > 2, lines))
lines = list(filter(lambda l: l.split('#')[1] == 'hum' + str(HUM_ID), lines))

entries: List[Entry] = []
for line in lines:
    fields = line.split('#')
    entries.append(Entry(int(fields[0]), int(fields[1].replace('hum', '')), float(fields[2])))

for entry in entries:
    entry.print()
